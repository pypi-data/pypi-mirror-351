#include "server.h"
#include "router.h"
#include "logging.h"
#include "windows_compat.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>
#include <Python.h>
#include <yyjson.h>

typedef struct {
    uv_write_t req;
    uv_buf_t buf;
    bool keep_alive;  // Track if connection should be kept alive
} write_req_t;

typedef struct {
    llhttp_t parser;
    uv_tcp_t client;
    catzilla_server_t* server;
    char url[CATZILLA_PATH_MAX];
    char method[CATZILLA_METHOD_MAX];
    char* body;
    size_t body_length;
    size_t body_size;
    content_type_t content_type;  // Keep this aligned with 4-byte boundary
    bool parsing_content_type;
    bool keep_alive;  // Track if client wants keep-alive
    bool parsing_connection;  // Track if we're parsing Connection header
    bool has_connection_header;  // Track if Connection header was sent
    char _padding[0];  // Add padding to ensure proper alignment
} client_context_t;

// Forward declarations
static void on_connection(uv_stream_t* server, int status);
static void alloc_buffer(uv_handle_t* handle, size_t suggested_size, uv_buf_t* buf);
static void on_read(uv_stream_t* client, ssize_t nread, const uv_buf_t* buf);
static void on_close(uv_handle_t* handle);
static void after_write(uv_write_t* req, int status);
static void signal_handler(uv_signal_t* handle, int signum);
static int on_message_complete(llhttp_t* parser);
static void send_response_with_connection(uv_stream_t* client, int status_code, const char* headers, const char* body, size_t body_len, bool keep_alive);
int parse_query_params(catzilla_request_t* request, const char* query_string);
void url_decode(const char* src, char* dst);

// Add a new function to get client context from client handle
static client_context_t* get_client_context(uv_stream_t* client) {
    if (!client) return NULL;
    return (client_context_t*)client->data;
}

// Global reference to the active server for signal handling
static catzilla_server_t* active_server = NULL;

static int on_message_begin(llhttp_t* parser) {
    client_context_t* context = (client_context_t*)parser->data;
    context->url[0] = '\0';
    context->method[0] = '\0';
    free(context->body);
    context->body = NULL;
    context->body_length = 0;
    context->body_size = 0;
    context->parsing_content_type = false;
    context->content_type = CONTENT_TYPE_NONE;  // Reset content type at start of message
    LOG_HTTP_DEBUG("Message begin: content type reset to NONE (type=%d)", (int)context->content_type);
    return 0;
}

static int on_url(llhttp_t* parser, const char* at, size_t length) {
    client_context_t* context = (client_context_t*)parser->data;

    // Store the full URL including query string
    if (length >= CATZILLA_PATH_MAX) length = CATZILLA_PATH_MAX - 1;
    memcpy(context->url, at, length);
    context->url[length] = '\0';
    LOG_HTTP_DEBUG("Received full URL: %s", context->url);
    return 0;
}

static int on_header_field(llhttp_t* parser, const char* at, size_t length) {
    client_context_t* context = (client_context_t*)parser->data;
    context->parsing_content_type = false;  // Reset flags by default
    context->parsing_connection = false;

    if (length == 12 && strncasecmp(at, "Content-Type", 12) == 0) {
        LOG_HTTP_DEBUG("Found Content-Type header");
        context->parsing_content_type = true;
    } else if (length == 10 && strncasecmp(at, "Connection", 10) == 0) {
        LOG_HTTP_DEBUG("Found Connection header");
        context->parsing_connection = true;
        context->has_connection_header = true;
    }
    return 0;
}

static int on_header_value(llhttp_t* parser, const char* at, size_t length) {
    client_context_t* context = (client_context_t*)parser->data;
    if (context->parsing_content_type) {
        LOG_HTTP_DEBUG("Processing Content-Type header: '%.*s'", (int)length, at);

        // Store content type for later use in JSON/form parsing
        content_type_t new_type = CONTENT_TYPE_NONE;

        if (length >= 16 && strncasecmp(at, "application/json", 16) == 0) {
            new_type = CONTENT_TYPE_JSON;
        } else if (length >= 33 && strncasecmp(at, "application/x-www-form-urlencoded", 33) == 0) {
            new_type = CONTENT_TYPE_FORM;
        }

        // Validate and set the content type
        if (new_type >= CONTENT_TYPE_NONE && new_type <= CONTENT_TYPE_FORM) {
            context->content_type = new_type;
            LOG_HTTP_DEBUG("Content-Type set to: %s (type=%d)",
                new_type == CONTENT_TYPE_JSON ? "application/json" :
                new_type == CONTENT_TYPE_FORM ? "application/x-www-form-urlencoded" : "none",
                (int)context->content_type);
        } else {
            context->content_type = CONTENT_TYPE_NONE;
            LOG_HTTP_DEBUG("Invalid content type, defaulting to NONE");
        }

        context->parsing_content_type = false;
    } else if (context->parsing_connection) {
        LOG_HTTP_DEBUG("Processing Connection header: '%.*s'", (int)length, at);

        // Check for keep-alive
        if (length >= 10 && strncasecmp(at, "keep-alive", 10) == 0) {
            context->keep_alive = true;
            LOG_HTTP_DEBUG("Connection: keep-alive detected");
        } else {
            context->keep_alive = false;
            LOG_HTTP_DEBUG("Connection: close or other");
        }

        context->parsing_connection = false;
    }
    return 0;
}

static int on_headers_complete(llhttp_t* parser) {
    client_context_t* context = (client_context_t*)parser->data;
    const char* method = llhttp_method_name(parser->method);
    size_t method_len = strlen(method);
    if (method_len >= CATZILLA_METHOD_MAX) method_len = CATZILLA_METHOD_MAX - 1;
    memcpy(context->method, method, method_len);
    context->method[method_len] = '\0';

    // HTTP/1.1 defaults to keep-alive if no Connection header was specified
    if (!context->has_connection_header && llhttp_get_http_major(parser) == 1 && llhttp_get_http_minor(parser) == 1) {
        context->keep_alive = true;
        LOG_HTTP_DEBUG("HTTP/1.1 defaulting to keep-alive");
    }

    return 0;
}

static int on_body(llhttp_t* parser, const char* at, size_t length) {
    client_context_t* context = (client_context_t*)parser->data;
    if (context->body == NULL) {
        context->body_size = length > 1024 ? length : 1024;
        context->body = malloc(context->body_size + 1);
        if (!context->body) return -1;
        context->body_length = 0;
    } else if (context->body_length + length > context->body_size) {
        size_t new_size = context->body_size * 2;
        char* new_body = realloc(context->body, new_size + 1);
        if (!new_body) return -1;
        context->body = new_body;
        context->body_size = new_size;
    }
    memcpy(context->body + context->body_length, at, length);
    context->body_length += length;
    context->body[context->body_length] = '\0';
    LOG_HTTP_DEBUG("Received body chunk: %zu bytes", length);
    return 0;
}

// Function to check if body parsing will fail due to unsupported content type
static bool should_return_415(client_context_t* context) {
    // Only return 415 if we have a body and the content type is unsupported
    if (!context->body || context->body_length == 0) {
        return false;  // No body, no problem
    }

    // For POST/PUT/PATCH requests with body, we expect a supported content type
    if (strcmp(context->method, "POST") == 0 ||
        strcmp(context->method, "PUT") == 0 ||
        strcmp(context->method, "PATCH") == 0) {

        // If we have a body but no recognizable content type, return 415
        if (context->content_type == CONTENT_TYPE_NONE) {
            LOG_HTTP_DEBUG("Request has body but unsupported content type");
            return true;
        }
    }

    return false;
}

// Function to populate request with path parameters from route match
static void populate_path_params(catzilla_request_t* request, const catzilla_route_match_t* match) {
    if (!request || !match) return;

    // Clear existing path parameters
    request->path_param_count = 0;
    request->has_path_params = false;

    // Copy path parameters from match
    for (int i = 0; i < match->param_count && i < CATZILLA_MAX_PATH_PARAMS; i++) {
        strncpy(request->path_params[i].name, match->params[i].name, CATZILLA_PARAM_NAME_MAX - 1);
        request->path_params[i].name[CATZILLA_PARAM_NAME_MAX - 1] = '\0';

        strncpy(request->path_params[i].value, match->params[i].value, CATZILLA_PATH_SEGMENT_MAX - 1);
        request->path_params[i].value[CATZILLA_PATH_SEGMENT_MAX - 1] = '\0';

        request->path_param_count++;
    }

    if (request->path_param_count > 0) {
        request->has_path_params = true;
        LOG_HTTP_DEBUG("Populated %d path parameters in request", request->path_param_count);
    }
}

// Universal Python route handler for advanced router
void catzilla_python_route_handler(uv_stream_t* client) {
    // This handler should never be called directly since Python routes
    // are handled via py_request_callback in on_message_complete
    LOG_SERVER_ERROR("catzilla_python_route_handler called directly - this should not happen");
    const char* body = "500 Internal Server Error";
    catzilla_send_response(client, 500, "text/plain", body, strlen(body));
}

// Python callback helper
PyObject* handle_request_in_server(PyObject* callback,
    PyObject* client_capsule,
    const char* method,
    const char* path,
    const char* body)
{
    if (!callback || !PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "Callback is not callable");
        return NULL;
    }

    // Create a request structure
    catzilla_request_t* request = malloc(sizeof(catzilla_request_t));
    if (!request) {
        PyErr_NoMemory();
        return NULL;
    }
    memset(request, 0, sizeof(catzilla_request_t));

    // Copy data into request
    strncpy(request->method, method, CATZILLA_METHOD_MAX-1);
    request->method[CATZILLA_METHOD_MAX-1] = '\0';
    strncpy(request->path, path, CATZILLA_PATH_MAX-1);
    request->path[CATZILLA_PATH_MAX-1] = '\0';

    // Parse query parameters if present
    const char* query = strchr(path, '?');
    if (query) {
        query++; // Skip the '?' character
        if (parse_query_params(request, query) == 0) {
            LOG_HTTP_DEBUG("Successfully parsed query parameters");
        } else {
            LOG_HTTP_DEBUG("Failed to parse query parameters");
        }
    }

    if (body) {
        request->body = strdup(body);
        request->body_length = strlen(body);
    }

    // Get the client context using our new helper function
    uv_stream_t* client = (uv_stream_t*)PyCapsule_GetPointer(client_capsule, "catzilla.client");
    client_context_t* context = get_client_context(client);

    if (context) {
        LOG_HTTP_DEBUG("Found client context, current content type: %d", (int)context->content_type);

        // Copy content type directly
        request->content_type = context->content_type;
        LOG_HTTP_DEBUG("Set request content_type from context: %d (%s)",
            (int)request->content_type,
            request->content_type == CONTENT_TYPE_JSON ? "application/json" :
            request->content_type == CONTENT_TYPE_FORM ? "application/x-www-form-urlencoded" : "none");

        // Pre-parse based on content type
        if (request->content_type == CONTENT_TYPE_JSON) {
            LOG_HTTP_DEBUG("Pre-parsing JSON content");
            if (catzilla_parse_json(request) == 0) {
                LOG_HTTP_DEBUG("JSON parsing successful");
            } else {
                LOG_HTTP_DEBUG("JSON parsing failed");
            }
        } else if (request->content_type == CONTENT_TYPE_FORM) {
            LOG_HTTP_DEBUG("Pre-parsing form content");
            if (catzilla_parse_form(request) == 0) {
                LOG_HTTP_DEBUG("Form parsing successful");
            } else {
                LOG_HTTP_DEBUG("Form parsing failed");
            }
        } else {
            LOG_HTTP_DEBUG("Unknown content type: %d", request->content_type);
        }
    } else {
        LOG_HTTP_DEBUG("No client context found, using NONE content type");
        request->content_type = CONTENT_TYPE_NONE;
    }

    // Create request capsule
    PyObject* request_capsule = PyCapsule_New(request, "catzilla.request", NULL);
    if (!request_capsule) {
        if (request->json_doc) yyjson_doc_free(request->json_doc);
        free(request->body);
        free(request);
        return NULL;
    }

    // Build arguments tuple: (client_capsule, method, path, body, request_capsule)
    PyObject* args = Py_BuildValue("(OsssO)", client_capsule, method, path, body ? body : "", request_capsule);
    if (!args) {
        Py_DECREF(request_capsule);
        if (request->json_doc) yyjson_doc_free(request->json_doc);
        free(request->body);
        free(request);
        return NULL;
    }

    // Call the Python function
    PyObject* result = PyObject_CallObject(callback, args);
    Py_DECREF(args);
    Py_DECREF(request_capsule);
    if (request->json_doc) yyjson_doc_free(request->json_doc);
    free(request->body);
    free(request);

    if (!result) {
        PyErr_Print();
        return NULL;
    }
    return result;
}

int catzilla_parse_json(catzilla_request_t* request) {
    if (!request || !request->body || request->body_length == 0) {
        LOG_HTTP_DEBUG("JSON parse failed: no request, body, or zero length");
        return -1;
    }

    // Check if already parsed
    if (request->is_json_parsed) {
        LOG_HTTP_DEBUG("JSON already parsed");
        return 0;
    }

    // Check content type - allow parsing if it's JSON type
    if (request->content_type != CONTENT_TYPE_JSON) {
        LOG_HTTP_DEBUG("JSON parse failed: wrong content type (%d)", request->content_type);
        return -1;
    }

    LOG_HTTP_DEBUG("Parsing JSON body: '%s'", request->body);

    // Initialize JSON fields
    if (request->json_doc) {
        yyjson_doc_free(request->json_doc);
    }
    request->json_doc = NULL;
    request->json_root = NULL;

    // Parse JSON using yyjson
    yyjson_read_flag flg = YYJSON_READ_NOFLAG;
    yyjson_read_err err;
    request->json_doc = yyjson_read_opts(request->body, request->body_length, flg, NULL, &err);

    if (!request->json_doc) {
        LOG_HTTP_DEBUG("JSON parse error: %s at position %zu", err.msg, err.pos);
        request->is_json_parsed = true;  // Mark as parsed even if failed
        return -1;
    }

    request->json_root = yyjson_doc_get_root(request->json_doc);
    if (!request->json_root) {
        LOG_HTTP_DEBUG("JSON parse error: no root object");
        yyjson_doc_free(request->json_doc);
        request->json_doc = NULL;
        request->is_json_parsed = true;  // Mark as parsed even if failed
        return -1;
    }

    LOG_HTTP_DEBUG("JSON parsed successfully");
    request->is_json_parsed = true;
    return 0;
}

int catzilla_parse_form(catzilla_request_t* request) {
    if (!request || !request->body || request->body_length == 0) {
        LOG_HTTP_DEBUG("Form parse failed: no request, body, or zero length");
        return -1;
    }

    // Check if already parsed
    if (request->is_form_parsed) {
        LOG_HTTP_DEBUG("Form data already parsed");
        return 0;
    }

    // Check content type - allow parsing if it's form type
    if (request->content_type != CONTENT_TYPE_FORM) {
        LOG_HTTP_DEBUG("Form parse failed: wrong content type (%d)", request->content_type);
        return -1;
    }

    LOG_HTTP_DEBUG("Parsing form data: '%s'", request->body);

    // Initialize form fields
    request->form_field_count = 0;
    for (int i = 0; i < CATZILLA_MAX_FORM_FIELDS; i++) {
        request->form_fields[i] = NULL;
        request->form_values[i] = NULL;
    }

    // Parse form data
    char* body = strdup(request->body);  // Create a copy we can modify
    if (!body) {
        LOG_HTTP_DEBUG("Form parse error: memory allocation failed");
        request->is_form_parsed = true;  // Mark as parsed even if failed
        return -1;
    }

    char* token;
    char* rest = body;

    while ((token = strtok_r(rest, "&", &rest))) {
        char* key = token;
        char* value = strchr(token, '=');

        if (value) {
            *value = '\0';  // Split key=value
            value++;

            // URL decode key and value
            char* decoded_key = malloc(strlen(key) + 1);
            char* decoded_value = malloc(strlen(value) + 1);

            if (!decoded_key || !decoded_value) {
                free(decoded_key);
                free(decoded_value);
                free(body);
                LOG_HTTP_DEBUG("Form parse error: memory allocation failed");
                request->is_form_parsed = true;  // Mark as parsed even if failed
                return -1;
            }

            // Simple URL decode (can be enhanced)
            url_decode(key, decoded_key);
            url_decode(value, decoded_value);

            LOG_HTTP_DEBUG("Form field: %s = %s", decoded_key, decoded_value);

            if (request->form_field_count < CATZILLA_MAX_FORM_FIELDS) {
                request->form_fields[request->form_field_count] = decoded_key;
                request->form_values[request->form_field_count] = decoded_value;
                request->form_field_count++;
            } else {
                free(decoded_key);
                free(decoded_value);
            break;
            }
        }
    }

    free(body);
    LOG_HTTP_DEBUG("Form parsed successfully with %d fields", request->form_field_count);
    request->is_form_parsed = true;
    return 0;
}

yyjson_val* catzilla_get_json(catzilla_request_t* request) {
    if (!request->is_json_parsed) {
        if (catzilla_parse_json(request) != 0) {
            return NULL;
        }
    }
    return request->json_root;
}

const char* catzilla_get_form_field(catzilla_request_t* request, const char* field) {
    if (!request->is_form_parsed) {
        if (catzilla_parse_form(request) != 0) {
            return NULL;
        }
    }

    for (int i = 0; i < request->form_field_count; i++) {
        if (strcmp(request->form_fields[i], field) == 0) {
            return request->form_values[i];
        }
    }
    return NULL;
}

// Get the content type as a string
const char* catzilla_get_content_type_str(catzilla_request_t* request) {
    if (!request) {
        LOG_HTTP_DEBUG("get_content_type_str: NULL request");
        return "";
    }

    content_type_t type = request->content_type;
    LOG_HTTP_DEBUG("get_content_type_str: type=%d", (int)type);

    switch (type) {
        case CONTENT_TYPE_JSON:
            LOG_HTTP_DEBUG("get_content_type_str: returning application/json");
            return "application/json";
        case CONTENT_TYPE_FORM:
            LOG_HTTP_DEBUG("get_content_type_str: returning application/x-www-form-urlencoded");
            return "application/x-www-form-urlencoded";
        case CONTENT_TYPE_NONE:
        default:
            LOG_HTTP_DEBUG("get_content_type_str: returning empty string");
            return "";
    }
}

// Helper function for URL decoding
void url_decode(const char* src, char* dst) {
    char a, b;
    while (*src) {
        if (*src == '%' && (a = src[1]) && (b = src[2]) && isxdigit(a) && isxdigit(b)) {
            if (a >= 'a') a -= 'a'-'A';
            if (a >= 'A') a -= ('A' - 10);
            else a -= '0';
            if (b >= 'a') b -= 'a'-'A';
            if (b >= 'A') b -= ('A' - 10);
            else b -= '0';
            *dst++ = 16 * a + b;
            src += 3;
        } else if (*src == '+') {
            *dst++ = ' ';
            src++;
        } else {
            *dst++ = *src++;
        }
    }
    *dst = '\0';
}

int catzilla_server_init(catzilla_server_t* server) {
    memset(server, 0, sizeof(*server));
    server->loop = uv_default_loop();
    if (!server->loop) return -1;

    int rc = uv_tcp_init(server->loop, &server->server);
    if (rc) return rc;
    server->server.data = server;

    // Initialize signal handler
    rc = uv_signal_init(server->loop, &server->sig_handle);
    if (rc) return rc;
    server->sig_handle.data = server;

    // Initialize advanced router
    rc = catzilla_router_init(&server->router);
    if (rc) {
        LOG_SERVER_ERROR("Failed to initialize advanced router");
        return rc;
    }

    llhttp_settings_init(&server->parser_settings);
    server->parser_settings.on_message_begin  = on_message_begin;
    server->parser_settings.on_url            = on_url;
    server->parser_settings.on_header_field   = on_header_field;
    server->parser_settings.on_header_value   = on_header_value;
    server->parser_settings.on_headers_complete = on_headers_complete;
    server->parser_settings.on_body           = on_body;
    server->parser_settings.on_message_complete = on_message_complete;

    server->route_count = 0;
    server->is_running = false;
    server->py_request_callback = NULL;

    // Set global reference for signal handling
    active_server = server;

    LOG_SERVER_INFO("Server initialized with advanced routing system");
    return 0;
}

void signal_handler(uv_signal_t* handle, int signum) {
    LOG_SERVER_INFO("Signal %d received, stopping server...", signum);
    catzilla_server_t* server = (catzilla_server_t*)handle->data;
    catzilla_server_stop(server);
}

void catzilla_server_cleanup(catzilla_server_t* server) {
    server->is_running = false;

    // Clean up advanced router
    catzilla_router_cleanup(&server->router);

    uv_close((uv_handle_t*)&server->server, NULL);
    uv_close((uv_handle_t*)&server->sig_handle, NULL);
    uv_run(server->loop, UV_RUN_DEFAULT);
    active_server = NULL;
}

int catzilla_server_listen(catzilla_server_t* server, const char* host, int port) {
    // Fallback to default host if NULL or empty
    const char* bind_host = (host != NULL && strlen(host) > 0) ? host : "0.0.0.0";

    struct sockaddr_in addr;
    int rc = uv_ip4_addr(bind_host, port, &addr);
    if (rc) {
        LOG_SERVER_ERROR("Failed to resolve %s:%d: %s", bind_host, port, uv_strerror(rc));
        return rc;
    }
    rc = uv_tcp_bind(&server->server, (const struct sockaddr*)&addr, 0);
    if (rc) {
        LOG_SERVER_ERROR("Bind %s:%d: %s", bind_host, port, uv_strerror(rc));
        return rc;
    }
    rc = uv_listen((uv_stream_t*)&server->server, 128, on_connection);
    if (rc) {
        LOG_SERVER_ERROR("Listen %s:%d: %s", bind_host, port, uv_strerror(rc));
        return rc;
    }

    // Set up signal handler for graceful shutdown
    rc = uv_signal_start(&server->sig_handle, signal_handler, SIGINT);
    if (rc) {
        LOG_SERVER_ERROR("Failed to set up signal handler: %s", uv_strerror(rc));
        return rc;
    }

    LOG_SERVER_INFO("Catzilla server listening on %s:%d", bind_host, port);
    LOG_SERVER_INFO("Press Ctrl+C to stop the server");

    server->is_running = true;
    return uv_run(server->loop, UV_RUN_DEFAULT);
}


void catzilla_server_stop(catzilla_server_t* server) {
    if (!server->is_running) return;

    LOG_SERVER_INFO("Stopping Catzilla server...");
    server->is_running = false;

    //  Stop the loop so the outer uv_run in listen() will exit
    uv_stop(server->loop);

    // Stop the signal handler but don't close it yet
    uv_signal_stop(&server->sig_handle);
    LOG_SERVER_INFO("Stopped signal handler...");

    // Walk and close all active handles
    // This will include server->server and server->sig_handle
    uv_walk(server->loop, (uv_walk_cb)uv_close, NULL);
    LOG_SERVER_INFO("Closing all active handles...");

    // Run the loop so that each close callback fires
    uv_run(server->loop, UV_RUN_DEFAULT);

    // 5) Finally, close the loop itself
    if (uv_loop_close(server->loop) != 0) {
        LOG_SERVER_WARN("uv_loop_close returned busy");
    }

    LOG_SERVER_INFO("Server stopped");
}

int catzilla_server_add_route(catzilla_server_t* server,
                             const char* method,
                             const char* path,
                             void* handler,
                             void* user_data) {
    if (!server || !method || !path) return -1;

    // Check for route conflicts and warn
    catzilla_server_check_route_conflicts(server, method, path);

    // Add to advanced router first
    uint32_t route_id = catzilla_router_add_route(&server->router, method, path, handler, user_data, false);
    if (route_id > 0) {
        LOG_ROUTER_DEBUG("Added route to advanced router: %s %s (ID: %u)", method, path, route_id);
        return 0;  // Success
    }

    // Fallback to legacy route table if advanced router fails
    if (server->route_count >= CATZILLA_MAX_ROUTES) {
        LOG_SERVER_ERROR("Maximum legacy routes reached (%d)", CATZILLA_MAX_ROUTES);
        return -1;
    }

    catzilla_route_t* route = &server->routes[server->route_count++];
    strncpy(route->method, method, CATZILLA_METHOD_MAX-1);
    route->method[CATZILLA_METHOD_MAX-1] = '\0';
    strncpy(route->path, path, CATZILLA_PATH_MAX-1);
    route->path[CATZILLA_PATH_MAX-1] = '\0';
    route->handler = handler;
    route->user_data = user_data;

    LOG_ROUTER_DEBUG("Added route to legacy table: %s %s", method, path);
    return 0;
}

void catzilla_server_set_request_callback(catzilla_server_t* server, void* callback) {
    server->py_request_callback = callback;
}

// Internal function that adds Connection headers based on client context
static void send_response_with_connection(uv_stream_t* client,
                                        int status_code,
                                        const char* headers,
                                        const char* body,
                                        size_t body_len,
                                        bool keep_alive) {
    write_req_t* req = malloc(sizeof(*req));
    if (!req) return;

    // Store keep_alive info in the request for after_write callback
    req->keep_alive = keep_alive;

    const char* status_text;
    switch (status_code) {
        case 200: status_text="OK";break;
        case 201: status_text="Created";break;
        case 204: status_text="No Content";break;
        case 400: status_text="Bad Request";break;
        case 404: status_text="Not Found";break;
        case 405: status_text="Method Not Allowed";break;
        case 415: status_text="Unsupported Media Type";break;
        case 500: status_text="Internal Server Error";break;
        default:  status_text="Unknown";break;
    }

    // Calculate required buffer size including Connection header
    size_t status_line_len = snprintf(NULL, 0, "HTTP/1.1 %d %s\r\n", status_code, status_text);
    size_t headers_len = headers ? strlen(headers) : 0;
    size_t connection_header_len = keep_alive ?
        strlen("Connection: keep-alive\r\n") :
        strlen("Connection: close\r\n");
    size_t separator_len = 2; // "\r\n" to separate headers from body
    size_t total_header_len = status_line_len + headers_len + connection_header_len + separator_len;

    char* response = malloc(total_header_len + body_len);
    if (!response) { free(req); return; }

    // Build the response
    int offset = 0;
    offset += snprintf(response + offset, total_header_len + body_len - offset,
                      "HTTP/1.1 %d %s\r\n", status_code, status_text);

    if (headers && headers_len > 0) {
        memcpy(response + offset, headers, headers_len);
        offset += headers_len;
    }

    // Add Connection header
    const char* connection_header = keep_alive ? "Connection: keep-alive\r\n" : "Connection: close\r\n";
    memcpy(response + offset, connection_header, connection_header_len);
    offset += connection_header_len;

    // Add separator between headers and body
    memcpy(response + offset, "\r\n", 2);
    offset += 2;

    // Add body
    if (body_len > 0) {
        memcpy(response + offset, body, body_len);
    }

    req->buf = uv_buf_init(response, total_header_len + body_len);
    uv_write(&req->req, client, &req->buf, 1, after_write);
}

void catzilla_send_response(uv_stream_t* client,
                           int status_code,
                           const char* headers,
                           const char* body,
                           size_t body_len) {
    // Get client context to determine keep-alive setting
    client_context_t* context = get_client_context(client);
    bool keep_alive = context ? context->keep_alive : false;
    send_response_with_connection(client, status_code, headers, body, body_len, keep_alive);
}

static void on_connection(uv_stream_t* server, int status) {
    if (status < 0) {
        LOG_SERVER_DEBUG("Connection error: %s", uv_strerror(status));
        return;
    }
    LOG_SERVER_DEBUG("New connection received");
    catzilla_server_t* srv = server->data;

    client_context_t* ctx = malloc(sizeof(*ctx));
    if (!ctx) return;

    // Initialize all fields to zero/NULL
    memset(ctx, 0, sizeof(*ctx));
    ctx->server = srv;
    ctx->content_type = CONTENT_TYPE_NONE;  // Explicitly set to NONE
    ctx->parsing_content_type = false;
    ctx->parsing_connection = false;
    ctx->has_connection_header = false;
    ctx->keep_alive = false;  // Default to close connection (HTTP/1.0 behavior)
    ctx->body = NULL;
    ctx->body_length = 0;
    ctx->body_size = 0;
    ctx->url[0] = '\0';
    ctx->method[0] = '\0';

    LOG_SERVER_DEBUG("Initialized client context with content_type=%d", (int)ctx->content_type);

    if (uv_tcp_init(srv->loop, &ctx->client) != 0) {
        free(ctx);
        return;
    }
    ctx->client.data = ctx;
    llhttp_init(&ctx->parser, HTTP_REQUEST, &srv->parser_settings);
    ctx->parser.data = ctx;

    if (uv_accept(server, (uv_stream_t*)&ctx->client) != 0) {
        uv_close((uv_handle_t*)&ctx->client, on_close);
        return;
    }
    uv_read_start((uv_stream_t*)&ctx->client, alloc_buffer, on_read);
}

static void alloc_buffer(uv_handle_t* handle, size_t suggested_size, uv_buf_t* buf) {
    buf->base = malloc(suggested_size);
    buf->len  = buf->base ? suggested_size : 0;
}

static void on_read(uv_stream_t* client, ssize_t nread, const uv_buf_t* buf) {
    client_context_t* ctx = client->data;
    if (nread > 0) {
        llhttp_errno_t err = llhttp_execute(&ctx->parser, buf->base, nread);
        if (err != HPE_OK) {
            LOG_SERVER_ERROR("HTTP parsing error: %s", llhttp_errno_name(err));
            catzilla_send_response(client, 400, "text/plain", "400 Bad Request", strlen("400 Bad Request"));
            uv_close((uv_handle_t*)client, on_close);
        }
    } else if (nread < 0 && nread != UV_EOF) {
        LOG_SERVER_ERROR("Read error: %s", uv_strerror(nread));
    }
    free(buf->base);
    if (nread < 0) uv_close((uv_handle_t*)client, on_close);
}

static void on_close(uv_handle_t* handle) {
    client_context_t* ctx = handle->data;
    if (ctx) {
    free(ctx->body);
    free(ctx);
    }
}

static void after_write(uv_write_t* req, int status) {
    if (status < 0) LOG_SERVER_DEBUG("Write error: %s", uv_strerror(status));

    write_req_t* wr = (write_req_t*)req;

    // Only close connection if keep_alive is false
    if (!wr->keep_alive) {
        LOG_SERVER_DEBUG("Closing connection (keep_alive=false)");
        uv_close((uv_handle_t*)req->handle, on_close);
    } else {
        LOG_SERVER_DEBUG("Keeping connection alive (keep_alive=true)");
        // Connection stays open for next request
        // The client context and parser will handle subsequent requests
    }

    free(wr->buf.base);
    free(wr);
}

static int on_message_complete(llhttp_t* parser) {
    client_context_t* context = (client_context_t*)parser->data;
    catzilla_server_t* server = context->server;

    LOG_HTTP_DEBUG("HTTP message complete");
    LOG_SERVER_INFO("Received request: Method=%s, URL=%s", context->method, context->url);

    // Extract path from URL (remove query string)
    char path[CATZILLA_PATH_MAX];
    char* query_start = strchr(context->url, '?');
    if (query_start) {
        size_t path_length = query_start - context->url;
        if (path_length >= CATZILLA_PATH_MAX) path_length = CATZILLA_PATH_MAX - 1;
        memcpy(path, context->url, path_length);
        path[path_length] = '\0';
    } else {
        strncpy(path, context->url, CATZILLA_PATH_MAX - 1);
        path[CATZILLA_PATH_MAX - 1] = '\0';
    }

    LOG_HTTP_DEBUG("Extracted path: %s", path);

    // Check for 415 Unsupported Media Type before routing
    if (should_return_415(context)) {
        const char* body = "415 Unsupported Media Type";
        send_response_with_connection((uv_stream_t*)&context->client, 415, "text/plain", body, strlen(body), context->keep_alive);
        return 0;
    }

    // 1) If Python callback is set, hand off to Python and return
    if (server->py_request_callback != NULL) {
        PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject* client_capsule = PyCapsule_New((void*)&context->client, "catzilla.client", NULL);
        if (!client_capsule) {
            PyErr_Print();
            send_response_with_connection((uv_stream_t*)&context->client, 500, "text/plain", "500 Internal Server Error", strlen("500 Internal Server Error"), context->keep_alive);
        } else {
            PyObject* result = handle_request_in_server(
                server->py_request_callback,
                client_capsule,
                context->method,
                context->url,
                context->body ? context->body : ""  // Handle NULL body case
            );
            Py_XDECREF(result);
            Py_DECREF(client_capsule);
        }
        PyGILState_Release(gstate);
        return 0;
    }

    // 2) Advanced router dispatch
    catzilla_route_match_t match;
    int match_result = catzilla_router_match(&server->router, context->method, path, &match);

    if (match_result == 0 && match.route != NULL) {
        // Route matched successfully
        LOG_ROUTER_DEBUG("Route matched with %d path parameters", match.param_count);

        // Log path parameters
        for (int i = 0; i < match.param_count; i++) {
            LOG_ROUTER_DEBUG("Path param: %s = %s",
                   match.params[i].name, match.params[i].value);
        }

        // Create request structure and populate path parameters
        catzilla_request_t request;
        memset(&request, 0, sizeof(request));
        strncpy(request.method, context->method, CATZILLA_METHOD_MAX - 1);
        strncpy(request.path, path, CATZILLA_PATH_MAX - 1);
        request.body = context->body;
        request.body_length = context->body_length;
        request.content_type = context->content_type;

        populate_path_params(&request, &match);

        // Call the handler
        void (*handler_fn)(uv_stream_t*) = match.route->handler;
        if (handler_fn != NULL) {
            handler_fn((uv_stream_t*)&context->client);
        } else {
            // Handler is NULL
            const char* body = "500 Internal Server Error: NULL handler";
            send_response_with_connection((uv_stream_t*)&context->client, 500, "text/plain", body, strlen(body), context->keep_alive);
        }
    } else {
        // Handle different error cases based on status code suggestion
        if (match.status_code == 405 && match.has_allowed_methods) {
            // Method not allowed - path exists but method is wrong
            char response_body[512];
            snprintf(response_body, sizeof(response_body),
                    "405 Method Not Allowed. Allowed methods: %s", match.allowed_methods);

            // Send 405 response with Allow header
            char headers[1024];
            const char* connection_header = context->keep_alive ? "keep-alive" : "close";
            snprintf(headers, sizeof(headers),
                    "HTTP/1.1 405 Method Not Allowed\r\n"
                    "Content-Type: text/plain\r\n"
                    "Content-Length: %zu\r\n"
                    "Allow: %s\r\n"
                    "Connection: %s\r\n\r\n",
                    strlen(response_body), match.allowed_methods, connection_header);

            // Send headers and body
            write_req_t* write_req = malloc(sizeof(write_req_t));
            if (write_req) {
                write_req->keep_alive = context->keep_alive;  // Set keep_alive flag
                size_t total_length = strlen(headers) + strlen(response_body);
                char* response = malloc(total_length + 1);
                if (response) {
                    strcpy(response, headers);
                    strcat(response, response_body);

                    write_req->buf = uv_buf_init(response, total_length);
                    uv_write((uv_write_t*)write_req, (uv_stream_t*)&context->client,
                            &write_req->buf, 1, after_write);
                } else {
                    free(write_req);
                    send_response_with_connection((uv_stream_t*)&context->client, 500, "text/plain",
                                         "500 Internal Server Error", strlen("500 Internal Server Error"), context->keep_alive);
                }
            } else {
                send_response_with_connection((uv_stream_t*)&context->client, 500, "text/plain",
                                     "500 Internal Server Error", strlen("500 Internal Server Error"), context->keep_alive);
            }
        } else {
            // 404 Not Found - no route matched
            const char* body = "404 Not Found";
            send_response_with_connection((uv_stream_t*)&context->client, 404, "text/plain", body, strlen(body), context->keep_alive);
        }
    }

    // 3) Fallback to legacy route dispatch for backward compatibility
    if (match_result != 0) {
        catzilla_route_t* matched = NULL;
        for (int i = 0; i < server->route_count; i++) {
            catzilla_route_t* route = &server->routes[i];
            bool method_ok = (route->method[0] == '*' || strcmp(route->method, context->method) == 0);
            bool path_ok   = (route->path[0]   == '*' || strcmp(route->path, path) == 0);
            if (method_ok && path_ok) {
                matched = route;
                break;
            }
        }

        if (matched) {
            LOG_ROUTER_DEBUG("Fallback to legacy route matched");
            void (*handler_fn)(uv_stream_t*) = matched->handler;
            if (handler_fn != NULL) {
                handler_fn((uv_stream_t*)&context->client);
            } else {
                const char* body = "500 Internal Server Error: NULL handler";
                send_response_with_connection((uv_stream_t*)&context->client, 500, "text/plain", body, strlen(body), context->keep_alive);
            }
        }
    }

    return 0;
}

int parse_query_params(catzilla_request_t* request, const char* query_string) {
    if (!request || !query_string) return -1;

    // Initialize query parameters
    request->query_param_count = 0;
    request->has_query_params = false;
    for (int i = 0; i < CATZILLA_MAX_QUERY_PARAMS; i++) {
        request->query_params[i] = NULL;
        request->query_values[i] = NULL;
    }

    LOG_HTTP_DEBUG("Parsing query string: %s", query_string);

    // Create a copy we can modify
    char* query = strdup(query_string);
    if (!query) return -1;

    char* token;
    char* rest = query;

    while ((token = strtok_r(rest, "&", &rest))) {
        char* key = token;
        char* value = strchr(token, '=');

        if (value) {
            *value = '\0';  // Split key=value
            value++;

            // URL decode key and value
            char* decoded_key = malloc(strlen(key) + 1);
            char* decoded_value = malloc(strlen(value) + 1);

            if (!decoded_key || !decoded_value) {
                free(decoded_key);
                free(decoded_value);
                free(query);
                return -1;
            }

            url_decode(key, decoded_key);
            url_decode(value, decoded_value);

            LOG_HTTP_DEBUG("Query param: %s = %s", decoded_key, decoded_value);

            if (request->query_param_count < CATZILLA_MAX_QUERY_PARAMS) {
                request->query_params[request->query_param_count] = decoded_key;
                request->query_values[request->query_param_count] = decoded_value;
                request->query_param_count++;
                request->has_query_params = true;
            } else {
                free(decoded_key);
                free(decoded_value);
                break;
            }
        }
    }

    free(query);
    LOG_HTTP_DEBUG("Query parsing complete with %d parameters", request->query_param_count);
    return 0;
}

const char* catzilla_get_query_param(catzilla_request_t* request, const char* param) {
    if (!request || !request->has_query_params || !param) return NULL;

    for (int i = 0; i < request->query_param_count; i++) {
        if (strcmp(request->query_params[i], param) == 0) {
            return request->query_values[i];
        }
    }
    return NULL;
}

// Route introspection and debugging functions

void catzilla_server_print_routes(catzilla_server_t* server) {
    if (!server) {
        LOG_SERVER_ERROR("Server is NULL");
        return;
    }

    LOG_SERVER_INFO("===== CATZILLA ROUTE INFORMATION =====");
    LOG_SERVER_INFO("Advanced Router Routes: %d", server->router.route_count);
    LOG_SERVER_INFO("Legacy Routes: %d", server->route_count);

    // Print advanced router routes
    if (server->router.route_count > 0) {
        LOG_SERVER_INFO("Advanced Router Routes:");
        catzilla_route_t* routes[100];  // Limit to 100 routes for display
        int route_count = catzilla_router_get_routes(&server->router, routes, 100);

        for (int i = 0; i < route_count; i++) {
            LOG_SERVER_INFO("  %d: %s %s -> %p (ID: %u)",
                   i + 1, routes[i]->method, routes[i]->path,
                   routes[i]->handler, routes[i]->id);
        }
    }

    // Print legacy routes
    if (server->route_count > 0) {
        LOG_SERVER_INFO("Legacy Routes:");
        for (int i = 0; i < server->route_count; i++) {
            LOG_SERVER_INFO("  %d: %s %s -> %p",
                   i + 1, server->routes[i].method, server->routes[i].path,
                   server->routes[i].handler);
        }
    }

    LOG_SERVER_INFO("========================================");
}

int catzilla_server_get_route_count(catzilla_server_t* server) {
    if (!server) return -1;
    return server->router.route_count + server->route_count;
}

int catzilla_server_has_route(catzilla_server_t* server, const char* method, const char* path) {
    if (!server || !method || !path) return -1;

    // Check advanced router
    catzilla_route_match_t match;
    int result = catzilla_router_match(&server->router, method, path, &match);
    if (result == 0 && match.route != NULL) {
        return 1;  // Route found
    }

    // Check legacy routes
    for (int i = 0; i < server->route_count; i++) {
        catzilla_route_t* route = &server->routes[i];
        bool method_ok = (route->method[0] == '*' || strcmp(route->method, method) == 0);
        bool path_ok   = (route->path[0]   == '*' || strcmp(route->path, path) == 0);
        if (method_ok && path_ok) {
            return 1;  // Route found
        }
    }

    return 0;  // Route not found
}

int catzilla_server_get_route_info(catzilla_server_t* server,
                                   const char* method,
                                   const char* path,
                                   char* match_info,
                                   size_t buffer_size) {
    if (!server || !method || !path || !match_info || buffer_size == 0) return -1;

    // Try advanced router first
    catzilla_route_match_t match;
    int result = catzilla_router_match(&server->router, method, path, &match);

    if (result == 0 && match.route != NULL) {
        // Route matched
        int written = snprintf(match_info, buffer_size,
            "MATCH: Advanced Router\n"
            "Route: %s %s -> %p (ID: %u)\n"
            "Parameters: %d\n",
            match.route->method, match.route->path,
            match.route->handler, match.route->id,
            match.param_count);

        // Add parameter details
        for (int i = 0; i < match.param_count && written < buffer_size - 1; i++) {
            int param_written = snprintf(match_info + written, buffer_size - written,
                "  %s = %s\n", match.params[i].name, match.params[i].value);
            if (param_written > 0) written += param_written;
        }

        return 0;
    } else if (match.status_code == 405 && match.has_allowed_methods) {
        // Method not allowed
        snprintf(match_info, buffer_size,
            "NO_MATCH: Method Not Allowed (405)\n"
            "Path exists but method '%s' not allowed\n"
            "Allowed methods: %s\n",
            method, match.allowed_methods);
        return 0;
    }

    // Check legacy routes
    for (int i = 0; i < server->route_count; i++) {
        catzilla_route_t* route = &server->routes[i];
        bool method_ok = (route->method[0] == '*' || strcmp(route->method, method) == 0);
        bool path_ok   = (route->path[0]   == '*' || strcmp(route->path, path) == 0);
        if (method_ok && path_ok) {
            snprintf(match_info, buffer_size,
                "MATCH: Legacy Router\n"
                "Route: %s %s -> %p\n",
                route->method, route->path, route->handler);
            return 0;
        }
    }

    // No match found
    snprintf(match_info, buffer_size,
        "NO_MATCH: Not Found (404)\n"
        "No route found for %s %s\n",
        method, path);

    return 0;
}

// Check for route conflicts in the server
void catzilla_server_check_route_conflicts(catzilla_server_t* server, const char* method, const char* path) {
    if (!server || !method || !path) return;

    // Check against existing routes in advanced router
    catzilla_route_t* routes[100];  // Limit check to 100 routes
    int route_count = catzilla_router_get_routes(&server->router, routes, 100);

    for (int i = 0; i < route_count; i++) {
        catzilla_route_t* existing = routes[i];

        // Exact match conflict
        if (strcmp(existing->method, method) == 0 && strcmp(existing->path, path) == 0) {
            LOG_SERVER_WARN("Route conflict: %s %s already exists (ID: %u)",
                   method, path, existing->id);
            continue;
        }

        // Check for overlapping patterns
        // TODO: More sophisticated pattern overlap detection could be added here
        if (strcmp(existing->method, method) == 0) {
            // Same method, check for path conflicts
            // For now, just warn about similar paths
            if (strstr(existing->path, path) || strstr(path, existing->path)) {
                if (strlen(existing->path) != strlen(path)) {  // Not exact match
                    LOG_SERVER_WARN("Potential route conflict: %s %s may overlap with %s %s",
                           method, path, existing->method, existing->path);
                }
            }
        }
    }

    // Check against legacy routes too
    for (int i = 0; i < server->route_count; i++) {
        catzilla_route_t* existing = &server->routes[i];

        if (strcmp(existing->method, method) == 0 && strcmp(existing->path, path) == 0) {
            LOG_SERVER_WARN("Route conflict with legacy route: %s %s already exists",
                   method, path);
        }
    }
}
