"""
Router Group tests for Catzilla framework

Tests the RouterGroup functionality for organizing routes
with shared prefixes, tags, and metadata.
"""

import pytest
from unittest.mock import Mock
from catzilla import App, Request, Response, JSONResponse, RouterGroup


class TestRouterGroup:
    """Test RouterGroup basic functionality"""

    def test_router_group_creation(self):
        """Test RouterGroup initialization"""
        group = RouterGroup()
        assert group.prefix == ""
        assert group.tags == []
        assert group.description == ""
        assert group.metadata == {}
        assert group.routes() == []

    def test_router_group_with_prefix(self):
        """Test RouterGroup with prefix"""
        group = RouterGroup("/api")
        assert group.prefix == "/api"

        # Test prefix normalization
        group2 = RouterGroup("api")
        assert group2.prefix == "/api"

        group3 = RouterGroup("/api/")
        assert group3.prefix == "/api"

        # Root prefix should remain empty
        group4 = RouterGroup("/")
        assert group4.prefix == ""

    def test_router_group_with_metadata(self):
        """Test RouterGroup with tags and metadata"""
        group = RouterGroup(
            "/api/v1",
            tags=["api", "v1"],
            description="API version 1",
            metadata={"version": "1.0.0"}
        )
        assert group.prefix == "/api/v1"
        assert group.tags == ["api", "v1"]
        assert group.description == "API version 1"
        assert group.metadata == {"version": "1.0.0"}

    def test_path_combination(self):
        """Test path combination with prefix"""
        group = RouterGroup("/api")

        # Test various path combinations
        assert group._combine_path("/users") == "/api/users"
        assert group._combine_path("users") == "/api/users"
        assert group._combine_path("/") == "/api"

        # Test with empty prefix
        empty_group = RouterGroup("")
        assert empty_group._combine_path("/users") == "/users"
        assert empty_group._combine_path("users") == "/users"

    def test_route_registration(self):
        """Test route registration in group"""
        group = RouterGroup("/api")

        @group.get("/users")
        def get_users(request):
            return JSONResponse({"users": []})

        @group.post("/users")
        def create_user(request):
            return JSONResponse({"user": "created"})

        routes = group.routes()
        assert len(routes) == 2

        # Check first route (GET)
        method1, path1, handler1, metadata1 = routes[0]
        assert method1 == "GET"
        assert path1 == "/api/users"
        assert handler1 == get_users
        assert metadata1["group_prefix"] == "/api"

        # Check second route (POST)
        method2, path2, handler2, metadata2 = routes[1]
        assert method2 == "POST"
        assert path2 == "/api/users"
        assert handler2 == create_user

    def test_all_http_methods(self):
        """Test all HTTP method decorators"""
        group = RouterGroup("/api")

        @group.get("/test")
        def get_handler(request):
            return {}

        @group.post("/test")
        def post_handler(request):
            return {}

        @group.put("/test")
        def put_handler(request):
            return {}

        @group.delete("/test")
        def delete_handler(request):
            return {}

        @group.patch("/test")
        def patch_handler(request):
            return {}

        routes = group.routes()
        assert len(routes) == 5

        methods = {route[0] for route in routes}
        assert methods == {"GET", "POST", "PUT", "DELETE", "PATCH"}

        # All should have the same path
        paths = {route[1] for route in routes}
        assert paths == {"/api/test"}

    def test_route_metadata_inheritance(self):
        """Test that routes inherit group metadata"""
        group = RouterGroup(
            "/api",
            tags=["api"],
            description="API routes",
            metadata={"api_version": "1.0"}
        )

        @group.get("/users", tags=["users"], description="Get all users")
        def get_users(request):
            return {}

        routes = group.routes()
        assert len(routes) == 1

        method, path, handler, metadata = routes[0]
        assert metadata["group_prefix"] == "/api"
        assert metadata["group_description"] == "API routes"
        assert metadata["tags"] == ["api", "users"]  # Combined tags
        assert metadata["description"] == "Get all users"
        assert metadata["api_version"] == "1.0"

    def test_multiple_routes_decorator(self):
        """Test route decorator with multiple methods"""
        group = RouterGroup("/api")

        @group.route("/test", methods=["GET", "POST"])
        def test_handler(request):
            return {}

        routes = group.routes()
        assert len(routes) == 2

        methods = {route[0] for route in routes}
        assert methods == {"GET", "POST"}


class TestRouterGroupNesting:
    """Test RouterGroup nesting and inclusion"""

    def test_group_include_group(self):
        """Test including one group in another"""
        users_group = RouterGroup("/users")

        @users_group.get("/")
        def list_users(request):
            return {}

        @users_group.get("/{user_id}")
        def get_user(request):
            return {}

        api_group = RouterGroup("/api")
        api_group.include_group(users_group)

        routes = api_group.routes()
        assert len(routes) == 2

        # Check that paths are properly combined
        paths = {route[1] for route in routes}
        assert "/api/users" in paths
        assert "/api/users/{user_id}" in paths

    def test_nested_group_path_parameters(self):
        """Test that path parameters work correctly in nested RouterGroups - regression test"""
        # This tests the specific bug that was fixed where nested groups
        # weren't preserving path prefixes correctly for parameter extraction

        # Create users group with dynamic route
        users_group = RouterGroup("/users")

        @users_group.get("/{user_id}")
        def get_user(request):
            return {"user_id": request.path_params.get("user_id")}

        @users_group.get("/{user_id}/profile")
        def get_user_profile(request):
            return {"user_id": request.path_params.get("user_id")}

        # Create posts group with dynamic route
        posts_group = RouterGroup("/posts")

        @posts_group.get("/{post_id}")
        def get_post(request):
            return {"post_id": request.path_params.get("post_id")}

        # Create API v1 group and include the user/post groups
        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(users_group)
        api_v1_group.include_group(posts_group)

        # Verify routes are constructed correctly
        routes = api_v1_group.routes()
        assert len(routes) == 3

        paths = {route[1] for route in routes}
        # These paths should include ALL nested prefixes
        assert "/api/v1/users/{user_id}" in paths
        assert "/api/v1/users/{user_id}/profile" in paths
        assert "/api/v1/posts/{post_id}" in paths

        # Verify none of the broken paths exist (paths that would result from the bug)
        broken_paths = {"/api/v1/{user_id}", "/api/v1/{post_id}", "/api/v1/profile"}
        assert not any(broken_path in paths for broken_path in broken_paths)

    def test_triple_nested_group_path_parameters(self):
        """Test path parameters in triple-nested RouterGroups"""
        # Create the deepest level group
        resource_group = RouterGroup("/resources")

        @resource_group.get("/{resource_id}")
        def get_resource(request):
            return {"resource_id": request.path_params.get("resource_id")}

        @resource_group.get("/{resource_id}/details")
        def get_resource_details(request):
            return {"resource_id": request.path_params.get("resource_id")}

        # Create middle level group
        v1_group = RouterGroup("/v1")
        v1_group.include_group(resource_group)

        # Create top level group
        api_group = RouterGroup("/api")
        api_group.include_group(v1_group)

        routes = api_group.routes()
        assert len(routes) == 2

        paths = {route[1] for route in routes}
        # Should preserve all three prefix levels
        assert "/api/v1/resources/{resource_id}" in paths
        assert "/api/v1/resources/{resource_id}/details" in paths

        # Verify the broken paths from the bug don't exist
        broken_paths = {"/api/v1/{resource_id}", "/api/{resource_id}"}
        assert not any(broken_path in paths for broken_path in broken_paths)

    def test_nested_groups_with_multiple_parameters(self):
        """Test nested groups with routes containing multiple path parameters"""
        # Create a group with multiple parameters
        complex_group = RouterGroup("/users")

        @complex_group.get("/{user_id}/posts/{post_id}/comments/{comment_id}")
        def get_comment(request):
            return {
                "user_id": request.path_params.get("user_id"),
                "post_id": request.path_params.get("post_id"),
                "comment_id": request.path_params.get("comment_id")
            }

        # Nest it in an API group
        api_group = RouterGroup("/api/v2")
        api_group.include_group(complex_group)

        routes = api_group.routes()
        assert len(routes) == 1

        method, path, handler, metadata = routes[0]
        # Should preserve all prefixes and all parameters
        expected_path = "/api/v2/users/{user_id}/posts/{post_id}/comments/{comment_id}"
        assert path == expected_path

        # Ensure broken path doesn't exist
        broken_path = "/api/v2/{user_id}/posts/{post_id}/comments/{comment_id}"
        assert path != broken_path

    def test_app_integration_with_nested_path_parameters(self):
        """Test full App integration with nested RouterGroup path parameters"""
        from catzilla import App

        app = App()

        # Create nested groups
        users_group = RouterGroup("/users")

        @users_group.get("/{user_id}")
        def get_user(request):
            return {"user_id": request.path_params.get("user_id")}

        api_group = RouterGroup("/api/v1")
        api_group.include_group(users_group)

        # Include in app
        app.include_routes(api_group)

        # Verify app has correct routes
        app_routes = app.routes()
        assert len(app_routes) == 1

        route = app_routes[0]
        assert route["path"] == "/api/v1/users/{user_id}"
        assert route["method"] == "GET"

    def test_deep_group_nesting(self):
        """Test deep nesting of groups"""
        resource_group = RouterGroup("/resource")

        @resource_group.get("/")
        def list_resources(request):
            return {}

        v1_group = RouterGroup("/v1")
        v1_group.include_group(resource_group)

        api_group = RouterGroup("/api")
        api_group.include_group(v1_group)

        routes = api_group.routes()
        assert len(routes) == 1

        method, path, handler, metadata = routes[0]
        assert path == "/api/v1/resource"  # /api + /v1 + /resource with correct prefix handling
        assert metadata["original_group_prefix"] == "/v1/resource"
        assert metadata["included_in_group"] == "/api"


class TestAppIntegration:
    """Test RouterGroup integration with App"""

    def test_app_include_routes(self):
        """Test App.include_routes functionality"""
        app = App()

        # Create a router group
        api_group = RouterGroup("/api/v1", tags=["api", "v1"])

        @api_group.get("/users")
        def get_users(request):
            return JSONResponse({"users": []})

        @api_group.post("/users")
        def create_user(request):
            return JSONResponse({"message": "User created"})

        @api_group.get("/users/{user_id}")
        def get_user(request):
            user_id = request.path_params.get("user_id")
            return JSONResponse({"user_id": user_id})

        # Include the group routes in the app
        app.include_routes(api_group)

        # Check that routes are registered in the app
        routes = app.routes()
        assert len(routes) == 3

        # Check specific routes
        paths = {r["path"] for r in routes}
        assert "/api/v1/users" in paths
        assert "/api/v1/users/{user_id}" in paths

        methods = {r["method"] for r in routes}
        assert "GET" in methods
        assert "POST" in methods

    def test_app_multiple_groups(self):
        """Test including multiple RouterGroups in an App"""
        app = App()

        # Users group
        users_group = RouterGroup("/api/users", tags=["users"])

        @users_group.get("/")
        def list_users(request):
            return JSONResponse({"users": []})

        @users_group.post("/")
        def create_user(request):
            return JSONResponse({"user": "created"})

        # Posts group
        posts_group = RouterGroup("/api/posts", tags=["posts"])

        @posts_group.get("/")
        def list_posts(request):
            return JSONResponse({"posts": []})

        @posts_group.get("/{post_id}")
        def get_post(request):
            return JSONResponse({"post_id": request.path_params.get("post_id")})

        # Include both groups
        app.include_routes(users_group)
        app.include_routes(posts_group)

        routes = app.routes()
        assert len(routes) == 4

        paths = {r["path"] for r in routes}
        assert "/api/users/" in paths
        assert "/api/posts/" in paths
        assert "/api/posts/{post_id}" in paths

    def test_app_group_with_regular_routes(self):
        """Test mixing RouterGroup routes with regular app routes"""
        app = App()

        # Regular app route
        @app.get("/health")
        def health_check(request):
            return JSONResponse({"status": "ok"})

        # RouterGroup routes
        api_group = RouterGroup("/api")

        @api_group.get("/users")
        def get_users(request):
            return JSONResponse({"users": []})

        app.include_routes(api_group)

        routes = app.routes()
        assert len(routes) == 2

        paths = {r["path"] for r in routes}
        assert "/health" in paths
        assert "/api/users" in paths

    def test_group_conflict_detection(self):
        """Test that RouterGroup routes trigger conflict detection"""
        app = App()

        # First group
        group1 = RouterGroup("/api")

        @group1.get("/users")
        def get_users_v1(request):
            return JSONResponse({"version": "v1"})

        app.include_routes(group1)

        # Second group with conflicting route
        group2 = RouterGroup("/api")

        @group2.get("/users")
        def get_users_v2(request):
            return JSONResponse({"version": "v2"})

        # This should warn about route conflict
        with pytest.warns(UserWarning):
            app.include_routes(group2)

    def test_empty_group_inclusion(self):
        """Test including an empty RouterGroup"""
        app = App()
        empty_group = RouterGroup("/api")

        # Should not raise any errors
        app.include_routes(empty_group)

        routes = app.routes()
        assert len(routes) == 0


class TestRouterGroupEdgeCases:
    """Test edge cases and error conditions"""

    def test_root_prefix_group(self):
        """Test RouterGroup with root prefix"""
        root_group = RouterGroup("/")

        @root_group.get("/test")
        def test_handler(request):
            return {}

        routes = root_group.routes()
        assert len(routes) == 1

        method, path, handler, metadata = routes[0]
        assert path == "/test"  # Should not double up slashes

    def test_complex_path_normalization(self):
        """Test complex path combinations and normalization"""
        group = RouterGroup("/api//v1/")  # Double slashes and trailing slash

        @group.get("//users//")
        def get_users(request):
            return {}

        routes = group.routes()
        method, path, handler, metadata = routes[0]
        # Should normalize to clean path
        assert "//" not in path
        assert path == "/api/v1/users"

    def test_group_with_dynamic_paths(self):
        """Test RouterGroup with dynamic path parameters"""
        group = RouterGroup("/api/v1")

        @group.get("/users/{user_id}")
        def get_user(request):
            return {"user_id": request.path_params.get("user_id")}

        @group.get("/users/{user_id}/posts/{post_id}")
        def get_user_post(request):
            return {
                "user_id": request.path_params.get("user_id"),
                "post_id": request.path_params.get("post_id")
            }

        routes = group.routes()
        assert len(routes) == 2

        paths = {route[1] for route in routes}
        assert "/api/v1/users/{user_id}" in paths
        assert "/api/v1/users/{user_id}/posts/{post_id}" in paths

    def test_group_overwrite_behavior(self):
        """Test overwrite behavior in RouterGroups"""
        group = RouterGroup("/api")

        @group.get("/test")
        def handler1(request):
            return {"version": 1}

        # Add another handler for the same route without overwrite
        @group.get("/test")
        def handler2(request):
            return {"version": 2}

        routes = group.routes()
        # Should have both routes registered (warning will be shown during app.include_routes)
        assert len(routes) == 2

        # Now with explicit overwrite
        @group.get("/test", overwrite=True)
        def handler3(request):
            return {"version": 3}

        routes = group.routes()
        assert len(routes) == 3

    def test_group_custom_metadata(self):
        """Test RouterGroup with custom metadata fields"""
        group = RouterGroup(
            "/api",
            custom_field="custom_value",
            middleware=["auth", "cors"],
            rate_limit=100
        )

        @group.get("/test", extra_field="test_value")
        def test_handler(request):
            return {}

        routes = group.routes()
        method, path, handler, metadata = routes[0]

        assert metadata["custom_field"] == "custom_value"
        assert metadata["middleware"] == ["auth", "cors"]
        assert metadata["rate_limit"] == 100
        assert metadata["extra_field"] == "test_value"


class TestRouterGroupRegression:
    """Test RouterGroup regression cases"""

    def test_exact_regression_api_v1_posts_bug(self):
        """Regression test for the exact bug: /api/v1/posts/45 returned post_id=None instead of '45'"""
        # This is the exact scenario that was broken before the fix

        # Create posts group with parameterized route
        posts_group = RouterGroup("/posts")

        @posts_group.get("/{post_id}")
        def get_post(request):
            # This should extract post_id correctly from the path
            post_id = request.path_params.get("post_id")
            return {"post": {"id": post_id}}

        # Create API v1 group and include posts group
        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(posts_group)

        # Verify the route path is constructed correctly
        routes = api_v1_group.routes()
        assert len(routes) == 1

        method, path, handler, metadata = routes[0]
        # The bug was that this became "/api/v1/{post_id}" instead of "/api/v1/posts/{post_id}"
        assert path == "/api/v1/posts/{post_id}", f"Expected '/api/v1/posts/{{post_id}}', got '{path}'"

        # Ensure the broken path doesn't exist
        assert path != "/api/v1/{post_id}", "Bug detected: path is missing '/posts' segment"

        # Verify metadata shows correct nesting
        # The route originates from posts_group, so group_prefix is from posts
        assert metadata["group_prefix"] == "/posts"
        # The original_group_prefix tracks where it was originally from
        assert metadata["original_group_prefix"] == "/posts"
        # The included_in_group shows which group it was included into
        assert metadata["included_in_group"] == "/api/v1"

    def test_multiple_nested_groups_regression(self):
        """Regression test for multiple nested groups in the same parent"""
        # Tests the scenario where multiple groups are nested in one parent
        # and ensures all preserve their prefixes correctly

        users_group = RouterGroup("/users")
        @users_group.get("/{user_id}")
        def get_user(request):
            return {"user_id": request.path_params.get("user_id")}

        posts_group = RouterGroup("/posts")
        @posts_group.get("/{post_id}")
        def get_post(request):
            return {"post_id": request.path_params.get("post_id")}

        comments_group = RouterGroup("/comments")
        @comments_group.get("/{comment_id}")
        def get_comment(request):
            return {"comment_id": request.path_params.get("comment_id")}

        # Include all in API v1 group
        api_group = RouterGroup("/api/v1")
        api_group.include_group(users_group)
        api_group.include_group(posts_group)
        api_group.include_group(comments_group)

        routes = api_group.routes()
        assert len(routes) == 3

        paths = {route[1] for route in routes}
        expected_paths = {
            "/api/v1/users/{user_id}",
            "/api/v1/posts/{post_id}",
            "/api/v1/comments/{comment_id}"
        }
        assert paths == expected_paths

        # Ensure none of the broken paths exist (the bug would create these)
        broken_paths = {"/api/v1/{user_id}", "/api/v1/{post_id}", "/api/v1/{comment_id}"}
        assert not any(broken_path in paths for broken_path in broken_paths)


class TestRouterGroupRegressionTests:
    """Regression tests for specific bugs that were fixed"""

    def test_exact_regression_api_v1_posts_bug(self):
        """
        Test the exact scenario that was broken before the fix:
        /api/v1/posts/45 should extract post_id="45" correctly

        This is a regression test for the bug where nested RouterGroups
        weren't preserving all prefix levels correctly.
        """
        # Create posts group - this is the inner group
        posts_group = RouterGroup("/posts")

        @posts_group.get("/")
        def list_posts(request):
            return {"posts": []}

        @posts_group.get("/{post_id}")
        def get_post(request):
            post_id = request.path_params.get("post_id")
            return {"post_id": post_id}

        # Create API v1 group - this is the outer group
        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(posts_group)

        # Verify the routes are constructed correctly
        routes = api_v1_group.routes()
        assert len(routes) == 2

        # Extract route information
        route_info = {route[1]: (route[0], route[2]) for route in routes}

        # Test that the exact problematic route exists with correct path
        assert "/api/v1/posts" in route_info
        assert "/api/v1/posts/{post_id}" in route_info

        # Verify the handlers are correct
        list_method, list_handler = route_info["/api/v1/posts"]
        detail_method, detail_handler = route_info["/api/v1/posts/{post_id}"]

        assert list_method == "GET"
        assert detail_method == "GET"
        assert list_handler == list_posts
        assert detail_handler == get_post

        # Verify the broken paths from the original bug don't exist
        broken_paths = ["/api/v1/{post_id}", "/api/v1/"]
        for broken_path in broken_paths:
            assert broken_path not in route_info, f"Broken path {broken_path} should not exist"

    def test_multiple_nested_groups_regression(self):
        """
        Test multiple groups nested in the same parent group.
        This ensures that each nested group maintains its own prefix correctly.
        """
        # Create multiple inner groups
        users_group = RouterGroup("/users")

        @users_group.get("/")
        def list_users(request):
            return {"users": []}

        @users_group.get("/{user_id}")
        def get_user(request):
            return {"user_id": request.path_params.get("user_id")}

        posts_group = RouterGroup("/posts")

        @posts_group.get("/")
        def list_posts(request):
            return {"posts": []}

        @posts_group.get("/{post_id}")
        def get_post(request):
            return {"post_id": request.path_params.get("post_id")}

        comments_group = RouterGroup("/comments")

        @comments_group.get("/{comment_id}")
        def get_comment(request):
            return {"comment_id": request.path_params.get("comment_id")}

        # Create outer group and include all inner groups
        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(users_group)
        api_v1_group.include_group(posts_group)
        api_v1_group.include_group(comments_group)

        # Verify all routes are constructed correctly
        routes = api_v1_group.routes()
        assert len(routes) == 5

        # Extract all paths
        paths = {route[1] for route in routes}

        # Verify all expected paths exist
        expected_paths = {
            "/api/v1/users",
            "/api/v1/users/{user_id}",
            "/api/v1/posts",
            "/api/v1/posts/{post_id}",
            "/api/v1/comments/{comment_id}"
        }
        assert paths == expected_paths

        # Verify none of the broken paths from the original bug exist
        broken_paths = {
            "/api/v1/{user_id}",
            "/api/v1/{post_id}",
            "/api/v1/{comment_id}",
            "/api/v1/"
        }
        assert not any(broken_path in paths for broken_path in broken_paths)

    def test_regression_parameter_extraction_simulation(self):
        """
        Simulate the actual parameter extraction that would happen in the router
        to ensure the paths are correct for parameter extraction.
        """
        # Create the same nested structure that was problematic
        posts_group = RouterGroup("/posts")

        @posts_group.get("/{post_id}")
        def get_post(request):
            return {"post_id": request.path_params.get("post_id")}

        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(posts_group)

        routes = api_v1_group.routes()

        # Find the route with post_id parameter
        post_route = None
        for method, path, handler, metadata in routes:
            if "{post_id}" in path:
                post_route = (method, path, handler, metadata)
                break

        assert post_route is not None, "Route with post_id parameter not found"

        method, path, handler, metadata = post_route

        # Verify the path is exactly what we expect for proper parameter extraction
        assert path == "/api/v1/posts/{post_id}"

        # The path should NOT be the broken version that would cause parameter extraction to fail
        assert path != "/api/v1/{post_id}"  # This was the broken path from the original bug

        # Verify metadata contains the correct group information
        assert "group_prefix" in metadata
        assert "original_group_prefix" in metadata or "included_in_group" in metadata


class TestNestedRouterGroupRegressionBug:
    """
    Regression tests for the specific bug where nested RouterGroups
    weren't extracting path parameters correctly.

    Original Issue:
    - Request to /api/v1/posts/45 resulted in post_id being None instead of "45"
    - Nested groups were dropping intermediate prefixes in path construction
    """

    def test_exact_bug_scenario_posts(self):
        """Test the exact bug scenario: /api/v1/posts/{post_id} parameter extraction"""
        # Create posts group (this was the problematic route)
        posts_group = RouterGroup("/posts")

        @posts_group.get("/{post_id}")
        def get_post(request):
            return {"post_id": request.path_params.get("post_id")}

        # Create API v1 group and include posts
        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(posts_group)

        routes = api_v1_group.routes()

        # Should have exactly one route
        assert len(routes) == 1

        method, path, handler, metadata = routes[0]

        # CRITICAL: Path must be correct for parameter extraction to work
        assert path == "/api/v1/posts/{post_id}"
        assert method == "GET"

        # Verify the broken path from the original bug does NOT exist
        assert path != "/api/v1/{post_id}"  # This was the bug!

    def test_exact_bug_scenario_users(self):
        """Test the exact bug scenario: /api/v1/users/{user_id} parameter extraction"""
        # Create users group
        users_group = RouterGroup("/users")

        @users_group.get("/{user_id}")
        def get_user(request):
            return {"user_id": request.path_params.get("user_id")}

        # Create API v1 group and include users
        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(users_group)

        routes = api_v1_group.routes()

        assert len(routes) == 1
        method, path, handler, metadata = routes[0]

        # CRITICAL: Path must preserve all nested prefixes
        assert path == "/api/v1/users/{user_id}"
        assert method == "GET"

        # The bug would have produced this incorrect path:
        assert path != "/api/v1/{user_id}"

    def test_multiple_nested_groups_parameter_isolation(self):
        """
        Test that multiple nested groups don't interfere with each other's parameters.
        This ensures the fix doesn't break parameter isolation between different groups.
        """
        # Create multiple groups with same parameter names but different contexts
        posts_group = RouterGroup("/posts")
        users_group = RouterGroup("/users")
        comments_group = RouterGroup("/comments")

        @posts_group.get("/{id}")
        def get_post(request):
            return {"type": "post", "id": request.path_params.get("id")}

        @users_group.get("/{id}")
        def get_user(request):
            return {"type": "user", "id": request.path_params.get("id")}

        @comments_group.get("/{id}")
        def get_comment(request):
            return {"type": "comment", "id": request.path_params.get("id")}

        # Include all in API v1
        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(posts_group)
        api_v1_group.include_group(users_group)
        api_v1_group.include_group(comments_group)

        routes = api_v1_group.routes()
        assert len(routes) == 3

        # Extract paths
        paths = {route[1] for route in routes}

        # All paths should be correctly formed with full prefixes
        expected_paths = {
            "/api/v1/posts/{id}",
            "/api/v1/users/{id}",
            "/api/v1/comments/{id}"
        }
        assert paths == expected_paths

        # None of the broken paths should exist
        broken_paths = {"/api/v1/{id}"}  # This would cause parameter ambiguity
        assert not any(broken_path in paths for broken_path in broken_paths)

    def test_deep_nesting_with_parameters_at_each_level(self):
        """
        Test deep nesting where each level has parameters.
        This is a more complex scenario that could expose edge cases in the fix.
        """
        # Deepest level: specific resource operations
        operations_group = RouterGroup("/operations")

        @operations_group.get("/{operation_id}")
        def get_operation(request):
            return {"operation_id": request.path_params.get("operation_id")}

        # Middle level: resource with ID
        resource_group = RouterGroup("/resources/{resource_id}")
        resource_group.include_group(operations_group)

        # Top level: API version
        api_v2_group = RouterGroup("/api/v2")
        api_v2_group.include_group(resource_group)

        routes = api_v2_group.routes()
        assert len(routes) == 1

        method, path, handler, metadata = routes[0]

        # Should preserve all nested parameters and prefixes
        assert path == "/api/v2/resources/{resource_id}/operations/{operation_id}"

        # Verify this is not any of the broken combinations the bug could have produced
        broken_paths = [
            "/api/v2/{operation_id}",  # Missing all intermediate levels
            "/api/v2/operations/{operation_id}",  # Missing resource level
            "/api/v2/{resource_id}/operations/{operation_id}",  # Missing 'resources' prefix
        ]
        assert path not in broken_paths

    def test_empty_prefix_edge_case(self):
        """
        Test edge case where some groups have empty prefixes.
        This ensures the fix handles prefix combination correctly even with empty prefixes.
        """
        # Group with empty prefix (root level routes)
        root_group = RouterGroup("")

        @root_group.get("/health")
        def health_check(request):
            return {"status": "ok"}

        @root_group.get("/status/{component}")
        def component_status(request):
            return {"component": request.path_params.get("component")}

        # Include in API group
        api_group = RouterGroup("/api")
        api_group.include_group(root_group)

        routes = api_group.routes()
        assert len(routes) == 2

        paths = {route[1] for route in routes}

        # Should properly handle empty prefix
        expected_paths = {
            "/api/health",
            "/api/status/{component}"
        }
        assert paths == expected_paths

    def test_regression_verification_with_app_integration(self):
        """
        Integration test that verifies the fix works end-to-end with the App class.
        This simulates the actual request routing that was failing.
        """
        # Create the problematic nested structure
        posts_group = RouterGroup("/posts")

        @posts_group.get("/{post_id}")
        def get_post(request):
            post_id = request.path_params.get("post_id")
            return JSONResponse({"post_id": post_id, "title": f"Post {post_id}"})

        api_v1_group = RouterGroup("/api/v1")
        api_v1_group.include_group(posts_group)

        # Create app and register the nested groups using the correct method
        app = App()
        app.include_routes(api_v1_group)

        # Verify the route was registered correctly in the app
        app_routes = app.routes()

        # The key test: verify that when the App processes the nested RouterGroup,
        # it creates the correct route path that will enable parameter extraction
        found_correct_route = False
        for route in app_routes:
            if route.get("path") == "/api/v1/posts/{post_id}":
                found_correct_route = True
                break

        # This assertion verifies that the App received the correctly fixed route
        # If the bug still existed, the App would receive "/api/v1/{post_id}" instead
        assert found_correct_route, "App did not receive the correctly constructed route path"

        # Additional verification: ensure the broken path is NOT registered
        broken_route_found = False
        for route in app_routes:
            if route.get("path") == "/api/v1/{post_id}":  # This was the broken path
                broken_route_found = True
                break

        assert not broken_route_found, "App incorrectly registered the broken route path from the original bug"
