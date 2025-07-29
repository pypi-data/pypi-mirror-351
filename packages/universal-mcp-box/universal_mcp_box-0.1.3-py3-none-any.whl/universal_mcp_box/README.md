# BoxApp MCP Server

An MCP Server for the BoxApp API.

## 🛠️ Tool List

This is automatically generated from OpenAPI schema for the BoxApp API.


| Tool | Description |
|------|-------------|
| `get_authorize` | Initiates an authorization flow using the GET method at the "/authorize" path, accepting parameters such as response type, client ID, redirect URI, state, and scope to manage user authentication and authorization. |
| `get_files_id` | Retrieves a file by its ID at the specified path "/files/{file_id}" using the GET method, allowing optional filtering by fields and headers for conditional requests. |
| `post_files_id` | Uploads or updates a file with the specified file_id and returns a status response, allowing optional field selection via a query parameter. |
| `put_files_id` | Updates or replaces the file specified by file_id using the provided data and returns the result. |
| `delete_files_id` | Deletes a file specified by its ID using the "DELETE" method at the "/files/{file_id}" path, returning success or error status codes based on the operation's outcome. |
| `get_files_id_app_item_associations` | Retrieves the list of application item associations linked to a specific file, allowing filtering by application type and pagination via limit and marker parameters. |
| `get_files_id_content` | Retrieves the content of a file specified by its file ID, allowing for partial downloads via range headers and authentication through access tokens. |
| `options_files_content` | Describes the communication options and supported operations available for the "/files/content" resource, including permitted HTTP methods and headers. |
| `post_files_upload_sessions` | Creates a new upload session for uploading large files in chunks, enabling reliable partial uploads and resumable file transfer. |
| `post_files_id_upload_sessions` | Creates an upload session for a file identified by the `file_id`, allowing for chunked file uploads. |
| `get_files_upload_sessions_id` | Retrieves information about a specific file upload session using the provided `upload_session_id`. |
| `delete_files_upload_sessions_id` | Deletes an upload session by its ID, discarding all uploaded data, using the DELETE method on the path "/files/upload_sessions/{upload_session_id}". |
| `get_files_upload_sessions_id_parts` | Retrieves a list of uploaded parts for a specified upload session, optionally paginated by offset and limit. |
| `post_files_upload_sessions_id_commit` | Commits a file upload session by finalizing and assembling all uploaded parts, completing the file upload process. |
| `post_files_id_copy` | Copies a specified file to a new location and returns the details of the copied file. |
| `get_files_id_thumbnail_id` | Retrieves a thumbnail image of a file specified by its ID, allowing for optional query parameters to set minimum and maximum dimensions, and returns the image in a specified extension. |
| `get_files_id_collaborations` | Retrieves a list of collaborations for a specified file using the Box API, allowing filtering by fields, limiting results, and using a marker for pagination. |
| `get_files_id_comments` | Retrieves a list of comments associated with a specific file, with options to filter, limit, and paginate the results. |
| `get_files_id_tasks` | Retrieves a list of tasks associated with a specific file identified by the `{file_id}` using the "GET" method. |
| `get_files_id_trash` | Retrieves information about a file specified by its ID and moves it to the trash or provides details about its trash status using the GET method. |
| `delete_files_id_trash` | Permanently deletes the specified file from the trash, removing it completely from the system. |
| `get_files_id_versions` | Retrieves a paginated list of versions for a specified file, allowing optional filtering and field selection. |
| `get_files_id_versions_id` | Retrieves the specified version of a file identified by `file_id` and `file_version_id`, allowing for optional filtering by specific fields. |
| `delete_files_id_versions_id` | Deletes a specific version of a file identified by its file ID and version ID, returning a successful status if the operation is completed. |
| `put_files_id_versions_id` | Updates a specific version of a file using the "PUT" method, identified by the file ID and version ID in the path "/files/{file_id}/versions/{file_version_id}". |
| `post_files_id_versions_current` | Creates a new version for the specified file, returning the details of the current version created. |
| `get_files_id_metadata` | Retrieves the metadata for a specific file identified by its `file_id` using the "GET" method. |
| `get_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo` | Retrieves the security classification metadata instance for the specified file from the Box enterprise metadata template. |
| `post_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo` | Applies a security classification to a file using the Box API by creating an instance of the `enterprise.securityClassification-6VMVochwUWo` metadata template for the specified file ID. |
| `delete_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo` | Deletes any enterprise security classifications from a specified file using the file ID. |
| `get_files_id_metadata_id_id` | Retrieves metadata for a specific file based on the file ID, scope, and template key using the GET method. |
| `delete_files_id_metadata_id_id` | Removes a metadata instance (identified by scope and template key) from the specified file, returning no content on success. |
| `get_files_id_metadata_global_box_skills_cards` | Retrieves the Box Skill cards metadata (such as keywords, transcripts, timelines, or statuses) associated with the specified file using the global boxSkillsCards metadata template. |
| `post_files_id_metadata_global_box_skills_cards` | Adds Box Skill cards to a file by creating new metadata at the specified file ID, allowing you to store and display processed data like keywords, transcripts, or status updates. |
| `delete_files_id_metadata_global_box_skills_cards` | Removes all Box Skills cards metadata from a specified file. |
| `get_files_id_watermark` | Retrieves the watermark information for a file specified by its ID, returning details about the applied watermark. |
| `put_files_id_watermark` | Applies a watermark to a file specified by its ID using the "PUT" method at the "/files/{file_id}/watermark" path. |
| `delete_files_id_watermark` | Removes the watermark from the specified file and returns an empty response if successful, or an error if no watermark exists[1]. |
| `get_file_requests_id` | Retrieves information about a specific file request by its ID using the "GET" method at the path "/file_requests/{file_request_id}". |
| `put_file_requests_id` | Updates a file request with the specified file_request_id using the PUT method, replacing the existing resource with new data if it exists, or creating a new one if it does not. |
| `delete_file_requests_id` | Deletes a specific file request identified by its ID and returns a success response if the operation is completed. |
| `post_file_requests_id_copy` | Copies an existing file request identified by its ID and applies it to a new folder, creating a duplicate of the original request. |
| `get_folders_id` | Retrieves detailed information about a specified folder, including its first 100 entries, using the Box API's GET method at the path "/folders/{folder_id}". |
| `post_folders_id` | Creates a new resource within a specific folder using the API, identified by the provided `folder_id`, and returns a status message upon successful creation. |
| `put_folders_id` | Updates an existing folder by replacing it entirely with new information, specified by the `folder_id` in the path, using the HTTP PUT method. |
| `delete_folders_id` | Deletes a folder with the specified ID, optionally removing all its contents recursively, and returns a status code indicating the success or failure of the operation. |
| `get_folders_id_app_item_associations` | Retrieves a list of application item associations for a specified folder using the "GET" method, allowing optional filtering by limit, marker, and application type. |
| `get_folders_id_items` | Retrieves a list of items within a specified Box folder using the "GET" method, returning files, folders, and web links based on the provided folder ID and optional query parameters for filtering and sorting. |
| `post_folders` | Creates a new folder using the POST method at the "/folders" path, allowing for optional specification of fields to include in the response. |
| `post_folders_id_copy` | Copies a specified folder with the given `folder_id` to a destination folder, creating a duplicate of the original folder's contents. |
| `get_folders_id_collaborations` | Retrieves a list of pending and active collaborations for a specified folder, returning all users who have access or have been invited to the folder[1][3][4]. |
| `get_folders_id_trash` | Retrieves the details of a specified folder that has been moved to the trash, including information about when it was trashed. |
| `delete_folders_id_trash` | Permanently deletes a folder (and its contents) from the trash, or if not already in the trash, moves the specified folder to the trash for eventual deletion. |
| `get_folders_id_metadata` | Retrieves metadata for a specific folder identified by its ID using the GET method. |
| `get_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo` | Retrieves the classification metadata instance applied to a specified folder, which includes security classifications set for the folder using the enterprise security classification template. |
| `post_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo` | Adds a security classification to a folder using the provided `folder_id` by specifying the classification label, utilizing the Box API. |
| `delete_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo` | Removes any security classifications from a specified folder using the Box Platform API. |
| `get_folders_id_metadata_id_id` | Retrieves metadata for a specific folder according to the specified scope and template key. |
| `delete_folders_id_metadata_id_id` | Deletes a metadata template instance from a specified folder using the provided folder ID, scope, and template key. |
| `get_folders_trash_items` | Retrieves a paginated list of items currently residing in the trash folder, supporting optional filtering, sorting, and field selection. |
| `get_folders_id_watermark` | Retrieves the watermark information for a specific folder using the folder ID. |
| `put_folders_id_watermark` | Applies a watermark to a specified folder using the Box API by sending a PUT request to the "/folders/{folder_id}/watermark" endpoint. |
| `delete_folders_id_watermark` | Deletes a watermark from a specified folder by its ID using the Box API. |
| `get_folder_locks` | Retrieves information about folder locks for a specified folder using its ID. |
| `post_folder_locks` | Creates a lock on a specified folder to prevent users from performing certain actions such as moving, deleting, or renaming the folder. |
| `delete_folder_locks_id` | Deletes a folder lock with the specified `folder_lock_id` in Box, requiring authentication as the folder's owner or co-owner. |
| `get_metadata_templates` | Retrieves a list of metadata templates, optionally filtered by a specific metadata instance ID, marker, and limit, using the GET method at the "/metadata_templates" path. |
| `get_metadata_templates_enterprise_security_classification_6_vmvochw_uwo_schema` | Retrieves the security classification metadata template schema, listing all available classification labels and their details for the enterprise. |
| `put_metadata_templates_enterprise_security_classification_6_vmvochw_uwo_schema_add` | Updates the labels and descriptions of one or more security classifications available to an enterprise using the Box API. |
| `get_metadata_templates_id_id_schema` | Retrieves the schema for a specific metadata template defined by the scope and template key using the "GET" method. |
| `delete_metadata_templates_id_id_schema` | Deletes a metadata template and its associated instances within a specified scope using the provided template key, returning a 204 No Content response upon successful removal. |
| `get_metadata_templates_id` | Retrieves specific details of a metadata template by its ID using the GET method at the "/metadata_templates/{template_id}" endpoint. |
| `get_metadata_templates_global` | Retrieves a list of all global metadata templates available to everyone using Box, regardless of their enterprise. |
| `get_metadata_templates_enterprise` | Retrieves a list of metadata templates for an enterprise using the Box API, allowing users to manage and access custom templates created within their organization. |
| `post_metadata_templates_schema` | Creates a metadata template by passing a scope, display name, and optional fields to define the structure of metadata, returning a created template upon successful execution. |
| `post_metadata_templates_schema_classifications` | Initializes the metadata template with a set of classifications at the specified path "/metadata_templates/schema#classifications" using the "POST" method. |
| `get_metadata_cascade_policies` | Retrieves a list of metadata cascade policies for a specified folder, using parameters such as folder ID, owner enterprise ID, and pagination controls like marker and offset. |
| `post_metadata_cascade_policies` | Creates a metadata cascade policy using the POST method at the "/metadata_cascade_policies" path, which automatically applies a metadata template instance to all files and folders within a specified folder. |
| `get_metadata_cascade_policies_id` | Retrieves the details of a specific metadata cascade policy, which describes how a metadata template instance is automatically applied to all files and folders within a targeted folder, using the provided policy ID. [1][2][4] |
| `delete_metadata_cascade_policies_id` | Deletes a specified metadata cascade policy, which stops the automatic cascading of metadata from a folder to its contents. |
| `post_metadata_cascade_policies_id_apply` | [LLM could not generate summary for POST /metadata_cascade_policies/{metadata_cascade_policy_id}/apply] |
| `post_metadata_queries_execute_read` | Executes a metadata query using SQL-like syntax to retrieve files and folders from Box based on specific metadata criteria via a POST request to the "/metadata_queries/execute_read" endpoint. |
| `get_comments_id` | Retrieves details of a specific comment by its ID, optionally returning only specified fields. |
| `put_comments_id` | Replaces or updates a comment with the specified comment_id using the provided data and returns a status indicating success or failure. |
| `delete_comments_id` | Deletes a comment identified by its unique `comment_id` using the HTTP DELETE method. |
| `post_comments` | Creates a new comment and allows specifying which fields to include in the response. |
| `get_collaborations_id` | Retrieves details of a specific collaboration identified by its unique ID, optionally filtering the returned fields as specified in the request. |
| `put_collaborations_id` | Updates a collaboration by replacing it with the data sent in the request body at the specified collaboration ID using the PUT method. |
| `delete_collaborations_id` | Deletes a collaboration specified by the `collaboration_id` using the DELETE method, returning an HTTP 204 response if successful. |
| `get_collaborations` | Retrieves a list of collaborations filtered by status, with optional fields and pagination, using the GET method at the "/collaborations" endpoint. |
| `post_collaborations` | Creates new collaborations using the POST method at the "/collaborations" path, allowing optional query parameters for specifying fields and notifications. |
| `get_search` | Searches GitHub resources using the "GET" method at the "/search" path, allowing for filtering by various parameters such as query, scope, file extensions, creation and update times, size range, and more to return relevant results. |
| `post_tasks` | Creates a new task and returns relevant details about the created task. |
| `get_tasks_id` | Retrieves a specific task identified by `{task_id}` using the GET method from the path "/tasks/{task_id}". |
| `put_tasks_id` | Replaces or updates an existing task with the provided data for the specified task_id. |
| `delete_tasks_id` | Deletes a task with the specified `task_id` using the HTTP DELETE method. |
| `get_tasks_id_assignments` | Retrieves the assignments for a specific task identified by the "{task_id}" using the GET method. |
| `post_task_assignments` | Creates a new task assignment and returns a task assignment object with a successful creation status. |
| `get_task_assignments_id` | Retrieves a specific task assignment by its ID using the GET method, returning details about the assignment if found, or an error if it does not exist. |
| `put_task_assignments_id` | Updates a task assignment with the specified ID using the PUT method. |
| `delete_task_assignments_id` | Deletes a task assignment by ID using the "DELETE" method, provided that the task assignment has no associated time entries. |
| `get_shared_items` | Retrieves information about shared items using a shared link via the Box API, allowing for optional specification of fields to include in the response. |
| `get_files_id_get_shared_link` | Retrieves a shared link for a specific file identified by its ID using the "GET" method. |
| `put_files_id_add_shared_link` | Generates a shared link for a specific file identified by `file_id`, optionally retrieving specified fields, using the PUT method at the path "/files/{file_id}#add_shared_link". |
| `put_files_id_update_shared_link` | Updates the shared link settings for a specific file using the PUT method, allowing modifications to access permissions and other link properties for the file identified by the file_id parameter. |
| `put_files_id_remove_shared_link` | Removes a shared link from a file using the Box API by setting the `shared_link` field to `null` via a PUT request to the specified file ID endpoint. |
| `get_shared_items_folders` | Retrieves a list of shared folder items using the Box API, with optional filtering by specified fields, and returns them in a formatted response. |
| `get_folders_id_get_shared_link` | Generates a shared link for a specific folder identified by the `{folder_id}` using the GET method, returning the link in the response. |
| `put_folders_id_add_shared_link` | Adds a shared link to a folder using the "PUT" method by specifying the folder ID in the URL and optionally customizing the response fields via query parameters. |
| `put_folders_id_update_shared_link` | Updates the shared link settings for a specified folder using the "PUT" method, returning a representation of the folder with the updated shared link. |
| `put_folders_id_remove_shared_link` | Removes a shared link from a specified folder using the Box API and returns a basic representation of the folder. |
| `post_web_links` | Submits a new web link to the server using the POST method at the "/web_links" path and returns a status message. |
| `get_web_links_id` | Retrieves information about a specific web link using its ID, identified by the path "/web_links/{web_link_id}", via a GET request. |
| `post_web_links_id` | Creates a new resource associated with a specific web link identified by `{web_link_id}` and returns a status message, optionally including specified fields. |
| `put_web_links_id` | Updates a web link resource identified by the `web_link_id` using the HTTP PUT method. |
| `delete_web_links_id` | Deletes a web link resource identified by its ID from the system using the DELETE method. |
| `get_web_links_id_trash` | Retrieves information about a trashed web link by its ID, allowing for optional specification of fields to include in the response. |
| `delete_web_links_id_trash` | Deletes a web link by moving it to the trash using the provided web link ID. |
| `get_shared_items_web_links` | Retrieves a list of web links for shared items using the GET method at the "/shared_items#web_links" endpoint. |
| `get_web_links_id_get_shared_link` | Retrieves details of a shared web link using its unique identifier and optional field selection parameters. |
| `put_web_links_id_add_shared_link` | Adds a shared link to a specified web link, allowing it to be accessed and shared by others, using the Box API. |
| `put_web_links_id_update_shared_link` | Updates a shared link for a web link identified by the `{web_link_id}` and optionally specifies fields to include in the response using the `fields` query parameter. |
| `put_web_links_id_remove_shared_link` | Removes a shared link from a web link resource using the `PUT` method by setting the shared link to null for the specified `web_link_id`. |
| `get_shared_items_app_items` | Retrieves information about a shared file or folder using a shared link provided in the `boxapi` header. |
| `get_users` | Retrieves a filtered or paginated list of users, supporting optional query parameters for filtering, field selection, and result pagination. |
| `post_users` | Creates a new user in the system using the "POST" method at the "/users" endpoint, allowing for dynamic management of user accounts. |
| `get_users_me` | Retrieves the current authenticated user's profile and allows filtering the response fields with an optional query parameter. |
| `post_users_terminate_sessions` | Terminates a user's active sessions by creating asynchronous jobs and returns the request status. |
| `get_users_id` | Retrieves details for a specific user identified by user_id, optionally filtering the returned fields. |
| `put_users_id` | Updates or replaces the details of a user identified by the provided user_id. |
| `delete_users_id` | Deletes a user by user ID, optionally notifying or forcing the deletion, and returns a successful status if the operation is completed. |
| `get_users_id_avatar` | Retrieves the avatar image for the specified user. |
| `delete_users_id_avatar` | Removes the avatar image associated with the specified user. |
| `put_users_id_folders_0` | Updates the details of the root folder (folder ID 0) for a specified user, optionally specifying fields to return and notification preferences. |
| `get_users_id_email_aliases` | Retrieves a list of email aliases for a specific user using the "GET" method, identified by their unique user ID. |
| `post_users_id_email_aliases` | Creates new email aliases for a specified user using the API endpoint at "/users/{user_id}/email_aliases". |
| `delete_users_id_email_aliases_id` | Deletes an email alias associated with a specific user, identified by the user ID and email alias ID, using the DELETE method. |
| `get_users_id_memberships` | Retrieves a paginated list of memberships associated with a specified user by user ID. |
| `post_invites` | Creates a new invite by sending a POST request to the /invites endpoint, optionally specifying fields to include in the response. |
| `get_invites_id` | Retrieves details about a specific invitation, identified by the `invite_id`, optionally including custom fields specified in the query parameters. |
| `get_groups` | Retrieves a list of groups, optionally filtered and paginated, based on query parameters for filtering, field selection, and result limits. |
| `post_groups` | Creates a new group using the API and returns a status message, with optional filtering by specified fields. |
| `post_groups_terminate_sessions` | Terminates active sessions for a specified group using a POST request to the "/groups/terminate_sessions" API endpoint. |
| `get_groups_id` | Retrieves detailed information about a specific group identified by the group_id, optionally filtering the returned data based on specified fields. |
| `put_groups_id` | Updates the details of a specific group identified by the group_id path parameter, with optional field selection via the fields query parameter, and returns a status response. |
| `delete_groups_id` | Deletes the group identified by the specified group ID. |
| `get_groups_id_memberships` | Retrieves a paginated list of memberships for a specified group by its group_id. |
| `get_groups_id_collaborations` | Retrieves a list of collaborations for a specified group, supporting pagination with optional limit and offset query parameters. |
| `post_group_memberships` | Creates a new group membership by adding an agent or user to a specified group. |
| `get_group_memberships_id` | Retrieves information about a specific group membership using the Zendesk API, returning details about the specified membership based on the provided `group_membership_id`. |
| `put_group_memberships_id` | Updates the details of a specific group membership identified by group_membership_id. |
| `delete_group_memberships_id` | Deletes a specific group membership identified by group_membership_id, removing the user from the group without returning content. |
| `get_webhooks` | Retrieves a paginated list of registered webhooks with optional marker and limit query parameters. |
| `post_webhooks` | Handles incoming webhook POST requests to receive, verify, and process event notifications from external systems. |
| `get_webhooks_id` | Retrieves detailed information about a specific webhook identified by its webhook_id. |
| `put_webhooks_id` | Updates an existing webhook with the specified ID using the PUT method, allowing modifications to the webhook's details. |
| `delete_webhooks_id` | Deletes a webhook specified by its ID using the DELETE method, allowing for the removal of unnecessary webhooks and optimizing system resources. |
| `put_skill_invocations_id` | Invokes or updates a skill with the specified ID using the PUT method, returning a response based on the operation's success or failure status. |
| `options_events` | Retrieves the communication options and supported HTTP methods available for the "/events" resource. |
| `get_events` | Retrieves a list of events based on specified filters such as stream type, stream position, event type, and creation time, using the "GET" method at the "/events" endpoint. |
| `get_collections` | Retrieves a list of collections with optional filtering by specified fields, starting from a given offset, and limited to a specified number of results using the "GET" method at the path "/collections". |
| `get_collections_id_items` | Retrieves a paginated list of items from a specified collection, optionally filtered by selected fields. |
| `get_collections_id` | Retrieves detailed information about a specific collection identified by the collection_id. |
| `get_recent_items` | Retrieves a list of recent items using the "GET" method at the "/recent_items" path, allowing customization with fields, limit, and marker parameters. |
| `get_retention_policies` | Retrieves a list of retention policies with optional filtering by name, type, creator, fields, limit, and pagination marker. |
| `post_retention_policies` | Creates a new data retention policy using the API and returns a relevant status message upon successful creation, handling potential errors for invalid requests or conflicts. |
| `get_retention_policies_id` | Retrieves detailed information about a specific data retention policy identified by its retention_policy_id. |
| `put_retention_policies_id` | Updates an existing data retention policy identified by its retention_policy_id to modify how data is retained and purged. |
| `delete_retention_policies_id` | Deletes a specified retention policy identified by retention_policy_id. |
| `get_retention_policies_id_assignments` | Retrieves a list of assignments for a specified retention policy, optionally filtered by type and including specified fields, with support for pagination. |
| `post_retention_policy_assignments` | Creates a new retention policy assignment using the "POST" method, specifying rules for retaining files based on folders or metadata, and returns a status message upon successful creation. |
| `get_retention_policy_assignments_id` | Retrieves the details of a specific retention policy assignment identified by the retention_policy_assignment_id. |
| `delete_retention_policy_assignments_id` | Deletes a retention policy assignment by ID using the DELETE method, removing the specified rule that retains files based on predefined conditions. |
| `get_retention_policy_assignments_id_files_under_retention` | Retrieves a paginated list of files currently under retention for a specified retention policy assignment. |
| `get_retention_policy_assignments_id_file_versions_under_retention` | Retrieves a list of file versions that are under retention, associated with a specified retention policy assignment, allowing for pagination via query parameters. |
| `get_legal_hold_policies` | Retrieves a list of legal hold policies filtered by optional parameters such as policy name, fields, pagination marker, and limit. |
| `post_legal_hold_policies` | Creates a new Legal Hold policy that can include specified restrictions to preserve relevant data for compliance or litigation purposes. |
| `get_legal_hold_policies_id` | Retrieves detailed information about a specific legal hold policy identified by its legal_hold_policy_id. |
| `put_legal_hold_policies_id` | Updates the details of an existing legal hold policy identified by the legal_hold_policy_id. |
| `delete_legal_hold_policies_id` | Deletes an existing legal hold policy asynchronously by its ID, initiating removal without immediate full deletion. |
| `get_legal_hold_policy_assignments` | Retrieves legal hold policy assignments based on specified parameters like policy ID, assignment type, and ID, allowing for pagination and customizable field selection. |
| `post_legal_hold_policy_assignments` | Creates a legal hold policy assignment that places a hold on specified users, folders, files, or file versions to preserve data for legal purposes. |
| `get_legal_hold_policy_assignments_id` | Retrieves the details of a specific legal hold policy assignment by its ID. |
| `delete_legal_hold_policy_assignments_id` | Deletes a legal hold policy assignment by its ID, initiating an asynchronous removal of the hold from the assigned item. |
| `get_legal_hold_policy_assignments_id_files_on_hold` | Retrieves the list of files currently on hold under a specific legal hold policy assignment. |
| `get_file_version_retentions` | Retrieves a list of file version retentions filtered by query parameters such as file ID, version ID, policy ID, disposition action, and date range. |
| `get_legal_hold_policy_assignments_id_file_versions_on_hold` | Retrieves a list of file versions currently on hold under a specified legal hold policy assignment. |
| `get_file_version_retentions_id` | Retrieves detailed information about a specific file version retention by its ID. |
| `get_file_version_legal_holds_id` | Retrieves details of a specific file version legal hold using its unique identifier. |
| `get_file_version_legal_holds` | Retrieves a list of legal holds applied to file versions, supporting pagination and filtering by policy ID. |
| `get_shield_information_barriers_id` | Retrieves detailed information about a specific shield information barrier identified by its ID. |
| `post_shield_information_barriers_change_status` | Changes the status of a specified shield information barrier using the POST method. |
| `get_shield_information_barriers` | Retrieves a list of shield information barriers using the GET method, allowing users to manage and access restrictions between user segments in Box, with optional parameters to control pagination via "marker" and "limit". |
| `post_shield_information_barriers` | Creates a shield information barrier to separate individuals or groups within the same firm, preventing the exchange of confidential information between them using the Box API. |
| `get_shield_information_barrier_reports` | Retrieves a paginated list of shield information barrier reports based on specified query parameters. |
| `post_shield_information_barrier_reports` | Creates a new shield information barrier report to track and manage data access restrictions between user segments. |
| `get_shield_information_barrier_reports_id` | Retrieves a specific shield information barrier report by its ID using the GET method. |
| `get_shield_information_barrier_segments_id` | Retrieves detailed information about a specific shield information barrier segment identified by its ID. |
| `delete_shield_information_barrier_segments_id` | Deletes a specific information barrier segment identified by its ID using the Box API. |
| `put_shield_information_barrier_segments_id` | Updates the properties of a specified shield information barrier segment identified by its ID. |
| `get_shield_information_barrier_segments` | Retrieves a list of shield information barrier segments filtered by the specified information barrier ID, with optional pagination parameters. |
| `post_shield_information_barrier_segments` | Creates a new shield information barrier segment to define a restricted communication boundary between user groups within an organization. |
| `get_shield_information_barrier_segment_members_id` | Retrieves a specific shield information barrier segment member by its ID using the GET method. |
| `delete_shield_information_barrier_segment_members_id` | Deletes a shield information barrier segment member identified by the given ID. |
| `get_shield_information_barrier_segment_members` | Retrieves a list of members for a specified shield information barrier segment using the Box API, allowing for pagination with optional marker and limit parameters. |
| `post_shield_information_barrier_segment_members` | Creates a new shield information barrier segment member using the Box API and returns a status message indicating the result of the operation. |
| `get_shield_information_barrier_segment_restrictions_id` | Retrieves detailed information about a specific shield information barrier segment restriction by its ID. |
| `delete_shield_information_barrier_segment_restrictions_id` | Deletes a specified shield information barrier segment restriction by its ID, removing the associated restriction from the system. |
| `get_shield_information_barrier_segment_restrictions` | Retrieves a list of segment restrictions for an information barrier segment specified by the `shield_information_barrier_segment_id` using the Box API. |
| `post_shield_information_barrier_segment_restrictions` | Creates a new shield information barrier segment restriction to control data access between defined segments. |
| `get_device_pinners_id` | Retrieves details for a specific device pinner using its unique identifier. |
| `delete_device_pinners_id` | Deletes a device pinner by ID using the DELETE method, identified by the path parameter "device_pinner_id". |
| `get_enterprises_id_device_pinners` | Retrieves a list of all device pins within a specified enterprise to manage and inspect devices authorized to access Box applications. |
| `get_terms_of_services` | Retrieves terms of service details based on the specified type using the GET method at the "/terms_of_services" path, with the type of terms of service passed as a query parameter named "tos_type." |
| `post_terms_of_services` | Submits terms of service data to the server using the POST method and returns a response indicating the result. |
| `get_terms_of_services_id` | Retrieves the details of a specific Terms of Service identified by the provided terms_of_service_id. |
| `put_terms_of_services_id` | Updates the terms of service identified by the given terms_of_service_id with new information. |
| `get_terms_of_service_user_statuses` | Retrieves a list of user statuses for a specified terms of service, including whether users have accepted the terms and when, using query parameters to filter by terms of service ID and user ID. |
| `post_terms_of_service_user_statuses` | Creates a new record tracking the acceptance status of a specific user for a terms of service agreement and returns a confirmation upon success. |
| `put_terms_of_service_user_statuses_id` | Updates the status of a user's acceptance for a specific Terms of Service using the given user status ID. |
| `get_collaboration_whitelist_entries` | Retrieves a paginated list of collaboration whitelist entries that specify allowed email domains for collaboration within the enterprise. |
| `post_collaboration_whitelist_entries` | Creates a collaboration whitelist entry to specify allowed domains and directions for repository collaboration. |
| `get_collaboration_whitelist_entries_id` | Retrieves information about a specific collaboration whitelist entry identified by its ID. |
| `delete_collaboration_whitelist_entries_id` | Deletes a specific collaboration whitelist entry identified by its ID using the DELETE method, returning a status code indicating successful removal. |
| `get_collaboration_whitelist_exempt_targets` | Retrieves a list of users who are exempt from the collaboration whitelist using the Box API. |
| `post_collaboration_whitelist_exempt_targets` | Creates a new collaboration whitelist exempt target, allowing specified users or entities to bypass collaboration whitelist domain restrictions. |
| `get_collaboration_whitelist_exempt_targets_id` | Retrieves details of a specific collaboration whitelist exempt target identified by its ID. |
| `delete_collaboration_whitelist_exempt_targets_id` | Removes a specific collaboration whitelist exemption by ID, revoking the target's exemption from domain restrictions using the Box API. |
| `get_storage_policies` | Retrieves a list of storage policies with optional filtering, pagination, and field selection parameters. |
| `get_storage_policies_id` | Retrieves detailed information about a specific storage policy identified by its storage_policy_id. |
| `get_storage_policy_assignments` | Retrieves a list of storage policy assignments with optional pagination and filtering by resolved type and ID. |
| `post_storage_policy_assignments` | Creates a new storage policy assignment to a user or enterprise. |
| `get_storage_policy_assignments_id` | Retrieves details of a specific storage policy assignment identified by its storage_policy_assignment_id. |
| `put_storage_policy_assignments_id` | Updates an existing storage policy assignment identified by storage_policy_assignment_id with new settings or configurations. |
| `delete_storage_policy_assignments_id` | Deletes a storage policy assignment identified by its ID, causing the user to inherit the enterprise's default storage policy. |
| `post_zip_downloads` | Creates a downloadable ZIP archive based on the provided input data and initiates the download process. |
| `get_zip_downloads_id_content` | Retrieves the content of a specific zip download identified by the `zip_download_id`. |
| `get_zip_downloads_id_status` | Retrieves the status of a specific zip download identified by the zip_download_id using the GET method. |
| `post_sign_requests_id_cancel` | Cancels an incomplete sign request using the provided sign request ID, preventing further signatures from being added. |
| `post_sign_requests_id_resend` | Resends a specified sign request identified by sign_request_id and returns a status indicating the outcome. |
| `get_sign_requests_id` | Retrieves the details of a specific sign request using the provided sign request identifier. |
| `get_sign_requests` | Retrieves a list of sign requests filtered by optional parameters such as marker, limit, senders, and shared requests. |
| `post_sign_requests` | Submits data to generate a signed request and returns a confirmation response. |
| `get_workflows` | Retrieves a list of workflows filtered by folder ID, trigger type, and pagination controls (limit and marker) using the GET method at the "/workflows" endpoint. |
| `post_workflows_id_start` | Starts the specified workflow identified by workflow_id via a POST request, triggering its execution without returning content. |
| `get_sign_templates` | Retrieves a list of sign templates, allowing pagination through the use of a marker and a limit parameter to control the number of results returned. |
| `get_sign_templates_id` | Retrieves details of a specific sign template identified by the provided `template_id` using the GET method. |
| `get_integration_mappings_slack` | Retrieves a list of Slack integration mappings with optional filtering by marker, limit, partner and Box item types and IDs, and manual creation status. |
| `post_integration_mappings_slack` | Creates a Slack integration mapping by associating a Slack channel with a Box item using the POST method. |
| `put_integration_mappings_slack_id` | Updates an existing Slack integration mapping by modifying the mapping identified by the specified `integration_mapping_id`. |
| `delete_integration_mappings_slack_id` | Deletes the Slack integration mapping identified by the integration_mapping_id, removing the link between the Slack channel and the Box folder without deleting either the folder or the channel. |
| `get_integration_mappings_teams` | Retrieves a list of Teams integration mappings in an enterprise, allowing filtering by partner item type, partner item ID, Box item ID, and Box item type. |
| `post_integration_mappings_teams` | Creates a Microsoft Teams integration mapping by linking a Teams channel to a Box item using the Box API. |
| `put_integration_mappings_teams_id` | Updates an existing Teams integration mapping identified by the provided `integration_mapping_id` using the Box API. |
| `delete_integration_mappings_teams_id` | Deletes a Teams integration mapping identified by the integration_mapping_id, removing the link between a Teams channel and a Box folder without deleting either resource. |
| `post_ai_ask` | Processes AI-based questions submitted via POST requests to provide relevant answers or responses. |
| `post_ai_text_gen` | Generates text based on a given prompt using a specified model, returning the generated text as a response. |
| `get_ai_agent_default` | Retrieves the default configuration settings for AI services, allowing clients to obtain parameters such as mode, language, and model for use or customization. |
| `post_ai_extract` | Extracts relevant data from specified sources using AI-powered text extraction techniques, returning clean and structured information based on the provided parameters. |
| `post_ai_extract_structured` | Extracts structured data from unstructured sources using AI-powered techniques, returning formatted data in a predefined schema. |
| `get_ai_agents` | Retrieves a filtered and paginated list of AI agents with optional parameters to specify mode, fields, agent state, inclusion of default box settings, marker, and limit. |
| `post_ai_agents` | Creates an AI agent instance using the POST method at the "/ai_agents" endpoint, enabling integration of AI functionalities into applications. |
| `put_ai_agents_id` | Updates the configuration or details of an AI agent identified by agent_id using the PUT method. |
| `get_ai_agents_id` | Retrieves information about a specific AI agent identified by its ID and optionally includes additional fields specified in the query parameters. |
| `delete_ai_agents_id` | Deletes an AI agent identified by the provided agent ID using the DELETE method and returns a status indicating the outcome of the operation. |
