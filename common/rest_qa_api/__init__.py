default_exclude_list = ["base_url", "resource", "allowed_methods"]

method_exclude_lists = {"get": ["post_data", "put_data", "patch_data", "delete_data"],
                        "post": ["params", "put_data", "patch_data", "delete_data"],
                        "put": ["params", "post_data", "patch_data", "delete_data"]}
