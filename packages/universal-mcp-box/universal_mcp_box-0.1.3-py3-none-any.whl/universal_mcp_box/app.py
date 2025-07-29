from typing import Any
from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration

class BoxApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name='box', integration=integration, **kwargs)
        self.base_url = "https://api.box.com/2.0"

    def get_authorize(self, response_type, client_id, redirect_uri=None, state=None, scope=None) -> Any:
        """
        Initiates an authorization flow using the GET method at the "/authorize" path, accepting parameters such as response type, client ID, redirect URI, state, and scope to manage user authentication and authorization.

        Args:
            response_type (string): The type of response we'd like to receive. Example: 'code'.
            client_id (string): The Client ID of the application that is requesting to authenticate
        the user. To get the Client ID for your application, log in to your
        Box developer console and click the **Edit Application** link for
        the application you're working with. In the OAuth 2.0 Parameters section
        of the configuration page, find the item labelled `client_id`. The
        text of that item is your application's Client ID. Example: 'ly1nj6n11vionaie65emwzk575hnnmrk'.
            redirect_uri (string): The URI to which Box redirects the browser after the user has granted
        or denied the application permission. This URI match one of the redirect
        URIs in the configuration of your application. It must be a
        valid HTTPS URI and it needs to be able to handle the redirection to
        complete the next step in the OAuth 2.0 flow.
        Although this parameter is optional, it must be a part of the
        authorization URL if you configured multiple redirect URIs
        for the application in the developer console. A missing parameter causes
        a `redirect_uri_missing` error after the user grants application access. Example: 'http://example.com/auth/callback'.
            state (string): A custom string of your choice. Box will pass the same string to
        the redirect URL when authentication is complete. This parameter
        can be used to identify a user on redirect, as well as protect
        against hijacked sessions and other exploits. Example: 'my_state'.
            scope (string): A space-separated list of application scopes you'd like to
        authenticate the user for. This defaults to all the scopes configured
        for the application in its configuration page. Example: 'admin_readwrite'.

        Returns:
            Any: Does not return any data, but rather should be used in the browser.

        Tags:
            Authorization
        """
        url = f"{self.base_url}/authorize"
        query_params = {k: v for k, v in [('response_type', response_type), ('client_id', client_id), ('redirect_uri', redirect_uri), ('state', state), ('scope', scope)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()


    def get_files_id(self, file_id, fields=None) -> dict[str, Any]:
        """
        Retrieves a file by its ID at the specified path "/files/{file_id}" using the GET method, allowing optional filtering by fields and headers for conditional requests.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Additionally this field can be used to query any metadata
        applied to the file by specifying the `metadata` field as well
        as the scope and key of the template to retrieve, for example
        `?fields=metadata.enterprise_12345.contractTemplate`. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a file object.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        Tags:
            Files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_files_id(self, file_id, fields=None, name=None, parent=None) -> dict[str, Any]:
        """
        Uploads or updates a file with the specified file_id and returns a status response, allowing optional field selection via a query parameter.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): An optional new name for the file. Example: 'Restored.docx'.
            parent (string): parent

        Returns:
            dict[str, Any]: Returns a file object when the file has been restored.

        Tags:
            Trashed files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'name': name,
            'parent': parent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_files_id(self, file_id, fields=None, name=None, description=None, parent=None, shared_link=None, lock=None, disposition_at=None, permissions=None, collections=None, tags=None) -> dict[str, Any]:
        """
        Updates or replaces the file specified by file_id using the provided data and returns the result.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): An optional different name for the file. This can be used to
        rename the file. Example: 'NewFile.txt'.
            description (string): The description for a file. This can be seen in the right-hand sidebar panel
        when viewing a file in the Box web app. Additionally, this index is used in
        the search index of the file, allowing users to find the file by the content
        in the description. Example: 'The latest reports. Automatically updated'.
            parent (string): parent
            shared_link (string): shared_link
            lock (object): Defines a lock on an item. This prevents the item from being
        moved, renamed, or otherwise changed by anyone other than the user
        who created the lock.

        Set this to `null` to remove the lock.
            disposition_at (string): The retention expiration timestamp for the given file. This
        date cannot be shortened once set on a file. Example: '2012-12-12T10:53:43-08:00'.
            permissions (object): Defines who can download a file.
            collections (array): An array of collections to make this file
        a member of. Currently
        we only support the `favorites` collection.

        To get the ID for a collection, use the
        [List all collections][1] endpoint.

        Passing an empty array `[]` or `null` will remove
        the file from all collections.

        [1]: e://get-collections
            tags (array): The tags for this item. These tags are shown in
        the Box web app and mobile apps next to an item.

        To add or remove a tag, retrieve the item's current tags,
        modify them, and then update this field.

        There is a limit of 100 tags per item, and 10,000
        unique tags per enterprise. Example: "['approved']".

        Returns:
            dict[str, Any]: Returns a file object.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        Tags:
            Files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'name': name,
            'description': description,
            'parent': parent,
            'shared_link': shared_link,
            'lock': lock,
            'disposition_at': disposition_at,
            'permissions': permissions,
            'collections': collections,
            'tags': tags,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_files_id(self, file_id) -> Any:
        """
        Deletes a file specified by its ID using the "DELETE" method at the "/files/{file_id}" path, returning success or error status codes based on the operation's outcome.

        Args:
            file_id (string): file_id

        Returns:
            Any: Returns an empty response when the file has been successfully
        deleted.

        Tags:
            Files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_app_item_associations(self, file_id, limit=None, marker=None, application_type=None) -> dict[str, Any]:
        """
        Retrieves the list of application item associations linked to a specific file, allowing filtering by application type and pagination via limit and marker parameters.

        Args:
            file_id (string): file_id
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            application_type (string): If given, only return app items for this application type Example: 'hubs'.

        Returns:
            dict[str, Any]: Returns a collection of app item objects. If there are no
        app items on this file, an empty collection will be returned.
        This list includes app items on ancestors of this File.

        Tags:
            App item associations
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/app_item_associations"
        query_params = {k: v for k, v in [('limit', limit), ('marker', marker), ('application_type', application_type)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_content(self, file_id, version=None, access_token=None) -> Any:
        """
        Retrieves the content of a file specified by its file ID, allowing for partial downloads via range headers and authentication through access tokens.

        Args:
            file_id (string): file_id
            version (string): The file version to download Example: '4'.
            access_token (string): An optional access token that can be used to pre-authenticate this request, which means that a download link can be shared with a browser or a third party service without them needing to know how to handle the authentication.
        When using this parameter, please make sure that the access token is sufficiently scoped down to only allow read access to that file and no other files or folders. Example: 'c3FIOG9vSGV4VHo4QzAyg5T1JvNnJoZ3ExaVNyQWw6WjRsanRKZG5lQk9qUE1BVQ'.

        Returns:
            Any: Returns the requested file if the client has the **follow
        redirects** setting enabled to automatically
        follow HTTP `3xx` responses as redirects. If not, the request
        will return `302` instead.
        For details, see
        the [download file guide](g://downloads/file#download-url).

        Tags:
            Downloads
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/content"
        query_params = {k: v for k, v in [('version', version), ('access_token', access_token)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def options_files_content(self, name=None, size=None, parent=None) -> dict[str, Any]:
        """
        Describes the communication options and supported operations available for the "/files/content" resource, including permitted HTTP methods and headers.

        Args:
            name (string): The name for the file Example: 'File.mp4'.
            size (integer): The size of the file in bytes Example: '1024'.
            parent (string): parent

        Returns:
            dict[str, Any]: If the check passed, the response will include a session URL that
        can be used to upload the file to.

        Tags:
            Files
        """
        request_body = {
            'name': name,
            'size': size,
            'parent': parent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/content"
        query_params = {}
        response = self._options(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()


    def post_files_upload_sessions(self, folder_id=None, file_size=None, file_name=None) -> dict[str, Any]:
        """
        Creates a new upload session for uploading large files in chunks, enabling reliable partial uploads and resumable file transfer.

        Args:
            folder_id (string): The ID of the folder to upload the new file to. Example: '0'.
            file_size (integer): The total number of bytes of the file to be uploaded Example: '104857600'.
            file_name (string): The name of new file Example: 'Project.mov'.

        Returns:
            dict[str, Any]: Returns a new upload session.

        Tags:
            Uploads (Chunked)
        """
        request_body = {
            'folder_id': folder_id,
            'file_size': file_size,
            'file_name': file_name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/upload_sessions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_files_id_upload_sessions(self, file_id, file_size=None, file_name=None) -> dict[str, Any]:
        """
        Creates an upload session for a file identified by the `file_id`, allowing for chunked file uploads.

        Args:
            file_id (string): file_id
            file_size (integer): The total number of bytes of the file to be uploaded Example: '104857600'.
            file_name (string): The optional new name of new file Example: 'Project.mov'.

        Returns:
            dict[str, Any]: Returns a new upload session.

        Tags:
            Uploads (Chunked)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'file_size': file_size,
            'file_name': file_name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}/upload_sessions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_upload_sessions_id(self, upload_session_id) -> dict[str, Any]:
        """
        Retrieves information about a specific file upload session using the provided `upload_session_id`.

        Args:
            upload_session_id (string): upload_session_id

        Returns:
            dict[str, Any]: Returns an upload session object.

        Tags:
            Uploads (Chunked)
        """
        if upload_session_id is None:
            raise ValueError("Missing required parameter 'upload_session_id'")
        url = f"{self.base_url}/files/upload_sessions/{upload_session_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()


    def delete_files_upload_sessions_id(self, upload_session_id) -> Any:
        """
        Deletes an upload session by its ID, discarding all uploaded data, using the DELETE method on the path "/files/upload_sessions/{upload_session_id}".

        Args:
            upload_session_id (string): upload_session_id

        Returns:
            Any: A blank response is returned if the session was
        successfully aborted.

        Tags:
            Uploads (Chunked)
        """
        if upload_session_id is None:
            raise ValueError("Missing required parameter 'upload_session_id'")
        url = f"{self.base_url}/files/upload_sessions/{upload_session_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_upload_sessions_id_parts(self, upload_session_id, offset=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of uploaded parts for a specified upload session, optionally paginated by offset and limit.

        Args:
            upload_session_id (string): upload_session_id
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a list of parts that have been uploaded.

        Tags:
            Uploads (Chunked)
        """
        if upload_session_id is None:
            raise ValueError("Missing required parameter 'upload_session_id'")
        url = f"{self.base_url}/files/upload_sessions/{upload_session_id}/parts"
        query_params = {k: v for k, v in [('offset', offset), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_files_upload_sessions_id_commit(self, upload_session_id, parts=None) -> dict[str, Any]:
        """
        Commits a file upload session by finalizing and assembling all uploaded parts, completing the file upload process.

        Args:
            upload_session_id (string): upload_session_id
            parts (array): The list details for the uploaded parts

        Returns:
            dict[str, Any]: Returns the file object in a list.

        Tags:
            Uploads (Chunked)
        """
        if upload_session_id is None:
            raise ValueError("Missing required parameter 'upload_session_id'")
        request_body = {
            'parts': parts,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/upload_sessions/{upload_session_id}/commit"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_files_id_copy(self, file_id, fields=None, name=None, version=None, parent=None) -> dict[str, Any]:
        """
        Copies a specified file to a new location and returns the details of the copied file.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): An optional new name for the copied file.

        There are some restrictions to the file name. Names containing
        non-printable ASCII characters, forward and backward slashes
        (`/`, `\`), and protected names like `.` and `..` are
        automatically sanitized by removing the non-allowed
        characters. Example: 'FileCopy.txt'.
            version (string): An optional ID of the specific file version to copy. Example: '0'.
            parent (object): The destination folder to copy the file to.

        Returns:
            dict[str, Any]: Returns a new file object representing the copied file.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        Tags:
            Files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'name': name,
            'version': version,
            'parent': parent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}/copy"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_thumbnail_id(self, file_id, extension, min_height=None, min_width=None, max_height=None, max_width=None) -> Any:
        """
        Retrieves a thumbnail image of a file specified by its ID, allowing for optional query parameters to set minimum and maximum dimensions, and returns the image in a specified extension.

        Args:
            file_id (string): file_id
            extension (string): extension
            min_height (integer): The minimum height of the thumbnail Example: '32'.
            min_width (integer): The minimum width of the thumbnail Example: '32'.
            max_height (integer): The maximum height of the thumbnail Example: '320'.
            max_width (integer): The maximum width of the thumbnail Example: '320'.

        Returns:
            Any: When a thumbnail can be created the thumbnail data will be
        returned in the body of the response.

        Tags:
            Files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        if extension is None:
            raise ValueError("Missing required parameter 'extension'")
        url = f"{self.base_url}/files/{file_id}/thumbnail.{extension}"
        query_params = {k: v for k, v in [('min_height', min_height), ('min_width', min_width), ('max_height', max_height), ('max_width', max_width)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_collaborations(self, file_id, fields=None, limit=None, marker=None) -> dict[str, Any]:
        """
        Retrieves a list of collaborations for a specified file using the Box API, allowing filtering by fields, limiting results, and using a marker for pagination.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.

        Returns:
            dict[str, Any]: Returns a collection of collaboration objects. If there are no
        collaborations on this file an empty collection will be returned.

        This list includes pending collaborations, for which the `status`
        is set to `pending`, indicating invitations that have been sent but not
        yet accepted.

        Tags:
            Collaborations (List)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/collaborations"
        query_params = {k: v for k, v in [('fields', fields), ('limit', limit), ('marker', marker)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_comments(self, file_id, fields=None, limit=None, offset=None) -> dict[str, Any]:
        """
        Retrieves a list of comments associated with a specific file, with options to filter, limit, and paginate the results.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of comment objects. If there are no
        comments on this file an empty collection will be returned.

        Tags:
            Comments
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/comments"
        query_params = {k: v for k, v in [('fields', fields), ('limit', limit), ('offset', offset)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_tasks(self, file_id) -> dict[str, Any]:
        """
        Retrieves a list of tasks associated with a specific file identified by the `{file_id}` using the "GET" method.

        Args:
            file_id (string): file_id

        Returns:
            dict[str, Any]: Returns a list of tasks on a file.

        If there are no tasks on this file an empty collection is returned
        instead.

        Tags:
            Tasks
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/tasks"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_trash(self, file_id, fields=None) -> dict[str, Any]:
        """
        Retrieves information about a file specified by its ID and moves it to the trash or provides details about its trash status using the GET method.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the file that was trashed,
        including information about when the it
        was moved to the trash.

        Tags:
            Trashed files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/trash"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_files_id_trash(self, file_id) -> Any:
        """
        Permanently deletes the specified file from the trash, removing it completely from the system.

        Args:
            file_id (string): file_id

        Returns:
            Any: Returns an empty response when the file was
        permanently deleted.

        Tags:
            Trashed files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/trash"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_versions(self, file_id, fields=None, limit=None, offset=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of versions for a specified file, allowing optional filtering and field selection.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.

        Returns:
            dict[str, Any]: Returns an array of past versions for this file.

        Tags:
            File versions
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/versions"
        query_params = {k: v for k, v in [('fields', fields), ('limit', limit), ('offset', offset)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_versions_id(self, file_id, file_version_id, fields=None) -> dict[str, Any]:
        """
        Retrieves the specified version of a file identified by `file_id` and `file_version_id`, allowing for optional filtering by specific fields.

        Args:
            file_id (string): file_id
            file_version_id (string): file_version_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a specific version of a file.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        Tags:
            File versions
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        if file_version_id is None:
            raise ValueError("Missing required parameter 'file_version_id'")
        url = f"{self.base_url}/files/{file_id}/versions/{file_version_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_files_id_versions_id(self, file_id, file_version_id) -> Any:
        """
        Deletes a specific version of a file identified by its file ID and version ID, returning a successful status if the operation is completed.

        Args:
            file_id (string): file_id
            file_version_id (string): file_version_id

        Returns:
            Any: Returns an empty response when the file has been successfully
        deleted.

        Tags:
            File versions
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        if file_version_id is None:
            raise ValueError("Missing required parameter 'file_version_id'")
        url = f"{self.base_url}/files/{file_id}/versions/{file_version_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_files_id_versions_id(self, file_id, file_version_id, trashed_at=None) -> dict[str, Any]:
        """
        Updates a specific version of a file using the "PUT" method, identified by the file ID and version ID in the path "/files/{file_id}/versions/{file_version_id}".

        Args:
            file_id (string): file_id
            file_version_id (string): file_version_id
            trashed_at (string): Set this to `null` to clear
        the date and restore the file.

        Returns:
            dict[str, Any]: Returns a restored file version object.

        Tags:
            File versions
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        if file_version_id is None:
            raise ValueError("Missing required parameter 'file_version_id'")
        request_body = {
            'trashed_at': trashed_at,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}/versions/{file_version_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_files_id_versions_current(self, file_id, fields=None, id=None, type=None) -> dict[str, Any]:
        """
        Creates a new version for the specified file, returning the details of the current version created.

        Args:
            file_id (string): file_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            id (string): The file version ID Example: '11446498'.
            type (string): The type to promote Example: 'file_version'.

        Returns:
            dict[str, Any]: Returns a newly created file version object.

        Tags:
            File versions
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'id': id,
            'type': type,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}/versions/current"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_metadata(self, file_id) -> dict[str, Any]:
        """
        Retrieves the metadata for a specific file identified by its `file_id` using the "GET" method.

        Args:
            file_id (string): file_id

        Returns:
            dict[str, Any]: Returns all the metadata associated with a file.

        This API does not support pagination and will therefore always return
        all of the metadata associated to the file.

        Tags:
            Metadata instances (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/metadata"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo(self, file_id) -> dict[str, Any]:
        """
        Retrieves the security classification metadata instance for the specified file from the Box enterprise metadata template.

        Args:
            file_id (string): file_id

        Returns:
            dict[str, Any]: Returns an instance of the `securityClassification` metadata
        template, which contains a `Box__Security__Classification__Key`
        field that lists all the classifications available to this
        enterprise.

        Tags:
            Classifications on files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo(self, file_id, Box__Security__Classification__Key=None) -> dict[str, Any]:
        """
        Applies a security classification to a file using the Box API by creating an instance of the `enterprise.securityClassification-6VMVochwUWo` metadata template for the specified file ID.

        Args:
            file_id (string): file_id
            Box__Security__Classification__Key (string): The name of the classification to apply to this file.

        To list the available classifications in an enterprise,
        use the classification API to retrieve the
        [classification template](e://get_metadata_templates_enterprise_securityClassification-6VMVochwUWo_schema)
        which lists all available classification keys. Example: 'Sensitive'.

        Returns:
            dict[str, Any]: Returns the classification template instance
        that was applied to the file.

        Tags:
            Classifications on files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'Box__Security__Classification__Key': Box__Security__Classification__Key,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo(self, file_id) -> Any:
        """
        Deletes any enterprise security classifications from a specified file using the file ID.

        Args:
            file_id (string): file_id

        Returns:
            Any: Returns an empty response when the classification is
        successfully deleted.

        Tags:
            Classifications on files
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_metadata_id_id(self, file_id, scope, template_key) -> dict[str, Any]:
        """
        Retrieves metadata for a specific file based on the file ID, scope, and template key using the GET method.

        Args:
            file_id (string): file_id
            scope (string): scope
            template_key (string): template_key

        Returns:
            dict[str, Any]: An instance of the metadata template that includes
        additional "key:value" pairs defined by the user or
        an application.

        Tags:
            Metadata instances (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        if scope is None:
            raise ValueError("Missing required parameter 'scope'")
        if template_key is None:
            raise ValueError("Missing required parameter 'template_key'")
        url = f"{self.base_url}/files/{file_id}/metadata/{scope}/{template_key}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()



    def delete_files_id_metadata_id_id(self, file_id, scope, template_key) -> Any:
        """
        Removes a metadata instance (identified by scope and template key) from the specified file, returning no content on success.

        Args:
            file_id (string): file_id
            scope (string): scope
            template_key (string): template_key

        Returns:
            Any: Returns an empty response when the metadata is
        successfully deleted.

        Tags:
            Metadata instances (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        if scope is None:
            raise ValueError("Missing required parameter 'scope'")
        if template_key is None:
            raise ValueError("Missing required parameter 'template_key'")
        url = f"{self.base_url}/files/{file_id}/metadata/{scope}/{template_key}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_metadata_global_box_skills_cards(self, file_id) -> dict[str, Any]:
        """
        Retrieves the Box Skill cards metadata (such as keywords, transcripts, timelines, or statuses) associated with the specified file using the global boxSkillsCards metadata template.

        Args:
            file_id (string): file_id

        Returns:
            dict[str, Any]: Returns all the metadata associated with a file.

        This API does not support pagination and will therefore always return
        all of the metadata associated to the file.

        Tags:
            Skills
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/metadata/global/boxSkillsCards"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_files_id_metadata_global_box_skills_cards(self, file_id, cards=None) -> dict[str, Any]:
        """
        Adds Box Skill cards to a file by creating new metadata at the specified file ID, allowing you to store and display processed data like keywords, transcripts, or status updates.

        Args:
            file_id (string): file_id
            cards (array): A list of Box Skill cards to apply to this file.

        Returns:
            dict[str, Any]: Returns the instance of the template that was applied to the file,
        including the data that was applied to the template.

        Tags:
            Skills
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'cards': cards,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}/metadata/global/boxSkillsCards"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()


    def delete_files_id_metadata_global_box_skills_cards(self, file_id) -> Any:
        """
        Removes all Box Skills cards metadata from a specified file.

        Args:
            file_id (string): file_id

        Returns:
            Any: Returns an empty response when the cards are
        successfully deleted.

        Tags:
            Skills
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/metadata/global/boxSkillsCards"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_watermark(self, file_id) -> dict[str, Any]:
        """
        Retrieves the watermark information for a file specified by its ID, returning details about the applied watermark.

        Args:
            file_id (string): file_id

        Returns:
            dict[str, Any]: Returns an object containing information about the
        watermark associated for to this file.

        Tags:
            Watermarks (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/watermark"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_files_id_watermark(self, file_id, watermark=None) -> dict[str, Any]:
        """
        Applies a watermark to a file specified by its ID using the "PUT" method at the "/files/{file_id}/watermark" path.

        Args:
            file_id (string): file_id
            watermark (object): The watermark to imprint on the file

        Returns:
            dict[str, Any]: Returns an updated watermark if a watermark already
        existed on this file.

        Tags:
            Watermarks (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'watermark': watermark,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}/watermark"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_files_id_watermark(self, file_id) -> Any:
        """
        Removes the watermark from the specified file and returns an empty response if successful, or an error if no watermark exists[1].

        Args:
            file_id (string): file_id

        Returns:
            Any: Removes the watermark and returns an empty response.

        Tags:
            Watermarks (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}/watermark"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_requests_id(self, file_request_id) -> dict[str, Any]:
        """
        Retrieves information about a specific file request by its ID using the "GET" method at the path "/file_requests/{file_request_id}".

        Args:
            file_request_id (string): file_request_id

        Returns:
            dict[str, Any]: Returns a file request object.

        Tags:
            File requests
        """
        if file_request_id is None:
            raise ValueError("Missing required parameter 'file_request_id'")
        url = f"{self.base_url}/file_requests/{file_request_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_file_requests_id(self, file_request_id, title=None, description=None, status=None, is_email_required=None, is_description_required=None, expires_at=None) -> dict[str, Any]:
        """
        Updates a file request with the specified file_request_id using the PUT method, replacing the existing resource with new data if it exists, or creating a new one if it does not.

        Args:
            file_request_id (string): file_request_id
            title (string): An optional new title for the file request. This can be
        used to change the title of the file request.

        This will default to the value on the existing file request. Example: 'Please upload required documents'.
            description (string): An optional new description for the file request. This can be
        used to change the description of the file request.

        This will default to the value on the existing file request. Example: 'Please upload required documents'.
            status (string): An optional new status of the file request.

        When the status is set to `inactive`, the file request
        will no longer accept new submissions, and any visitor
        to the file request URL will receive a `HTTP 404` status
        code.

        This will default to the value on the existing file request. Example: 'active'.
            is_email_required (boolean): Whether a file request submitter is required to provide
        their email address.

        When this setting is set to true, the Box UI will show
        an email field on the file request form.

        This will default to the value on the existing file request. Example: 'True'.
            is_description_required (boolean): Whether a file request submitter is required to provide
        a description of the files they are submitting.

        When this setting is set to true, the Box UI will show
        a description field on the file request form.

        This will default to the value on the existing file request. Example: 'True'.
            expires_at (string): The date after which a file request will no longer accept new
        submissions.

        After this date, the `status` will automatically be set to
        `inactive`.

        This will default to the value on the existing file request. Example: '2020-09-28T10:53:43-08:00'.

        Returns:
            dict[str, Any]: Returns the updated file request object.

        Tags:
            File requests
        """
        if file_request_id is None:
            raise ValueError("Missing required parameter 'file_request_id'")
        request_body = {
            'title': title,
            'description': description,
            'status': status,
            'is_email_required': is_email_required,
            'is_description_required': is_description_required,
            'expires_at': expires_at,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/file_requests/{file_request_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_file_requests_id(self, file_request_id) -> Any:
        """
        Deletes a specific file request identified by its ID and returns a success response if the operation is completed.

        Args:
            file_request_id (string): file_request_id

        Returns:
            Any: Returns an empty response when the file request has been successfully
        deleted.

        Tags:
            File requests
        """
        if file_request_id is None:
            raise ValueError("Missing required parameter 'file_request_id'")
        url = f"{self.base_url}/file_requests/{file_request_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_file_requests_id_copy(self, file_request_id, title=None, description=None, status=None, is_email_required=None, is_description_required=None, expires_at=None, folder=None) -> dict[str, Any]:
        """
        Copies an existing file request identified by its ID and applies it to a new folder, creating a duplicate of the original request.

        Args:
            file_request_id (string): file_request_id
            title (string): An optional new title for the file request. This can be
        used to change the title of the file request.

        This will default to the value on the existing file request. Example: 'Please upload required documents'.
            description (string): An optional new description for the file request. This can be
        used to change the description of the file request.

        This will default to the value on the existing file request. Example: 'Please upload required documents'.
            status (string): An optional new status of the file request.

        When the status is set to `inactive`, the file request
        will no longer accept new submissions, and any visitor
        to the file request URL will receive a `HTTP 404` status
        code.

        This will default to the value on the existing file request. Example: 'active'.
            is_email_required (boolean): Whether a file request submitter is required to provide
        their email address.

        When this setting is set to true, the Box UI will show
        an email field on the file request form.

        This will default to the value on the existing file request. Example: 'True'.
            is_description_required (boolean): Whether a file request submitter is required to provide
        a description of the files they are submitting.

        When this setting is set to true, the Box UI will show
        a description field on the file request form.

        This will default to the value on the existing file request. Example: 'True'.
            expires_at (string): The date after which a file request will no longer accept new
        submissions.

        After this date, the `status` will automatically be set to
        `inactive`.

        This will default to the value on the existing file request. Example: '2020-09-28T10:53:43-08:00'.
            folder (object): The folder to associate the new file request to.

        Returns:
            dict[str, Any]: Returns updated file request object.

        Tags:
            File requests
        """
        if file_request_id is None:
            raise ValueError("Missing required parameter 'file_request_id'")
        request_body = {
            'title': title,
            'description': description,
            'status': status,
            'is_email_required': is_email_required,
            'is_description_required': is_description_required,
            'expires_at': expires_at,
            'folder': folder,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/file_requests/{file_request_id}/copy"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id(self, folder_id, fields=None, sort=None, direction=None, offset=None, limit=None) -> dict[str, Any]:
        """
        Retrieves detailed information about a specified folder, including its first 100 entries, using the Box API's GET method at the path "/folders/{folder_id}".

        Args:
            folder_id (string): folder_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Additionally this field can be used to query any metadata
        applied to the file by specifying the `metadata` field as well
        as the scope and key of the template to retrieve, for example
        `?fields=metadata.enterprise_12345.contractTemplate`. Example: "['id', 'type', 'name']".
            sort (string): Defines the **second** attribute by which items
        are sorted. The folder type affects the way the items
        are sorted: * **Standard folder**: Items are always sorted by their `type` first, with folders listed before files, and files listed before web links. * **Root folder**: This parameter is not supported for marker-based pagination on the root folder (the folder with an `id` of `0`). * **Shared folder with parent path to the associated folder visible to the collaborator**: Items are always sorted by their `type` first, with folders listed before files, and files listed before web links. Example: 'id'.
            direction (string): The direction to sort results in. This can be either in alphabetical ascending
        (`ASC`) or descending (`DESC`) order. Example: 'ASC'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a folder, including the first 100 entries in the folder.
        If you used query parameters like
        `sort`, `direction`, `offset`, or `limit`
        the *folder items list* will be affected accordingly.

        To fetch more items within the folder, use the
        [Get items in a folder](e://get-folders-id-items)) endpoint.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        Tags:
            Folders, important
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}"
        query_params = {k: v for k, v in [('fields', fields), ('sort', sort), ('direction', direction), ('offset', offset), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folders_id(self, folder_id, fields=None, name=None, parent=None) -> dict[str, Any]:
        """
        Creates a new resource within a specific folder using the API, identified by the provided `folder_id`, and returns a status message upon successful creation.

        Args:
            folder_id (string): folder_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): An optional new name for the folder. Example: 'Restored Photos'.
            parent (string): parent

        Returns:
            dict[str, Any]: Returns a folder object when the folder has been restored.

        Tags:
            Trashed folders, important
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        request_body = {
            'name': name,
            'parent': parent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folder_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_folders_id(self, folder_id, fields=None, name=None, description=None, sync_state=None, can_non_owners_invite=None, parent=None, shared_link=None, folder_upload_email=None, tags=None, is_collaboration_restricted_to_enterprise=None, collections=None, can_non_owners_view_collaborators=None) -> dict[str, Any]:
        """
        Updates an existing folder by replacing it entirely with new information, specified by the `folder_id` in the path, using the HTTP PUT method.

        Args:
            folder_id (string): folder_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): The optional new name for this folder. Example: 'New Folder'.
            description (string): The optional description of this folder Example: 'Legal contracts for the new ACME deal'.
            sync_state (string): Specifies whether a folder should be synced to a
        user's device or not. This is used by Box Sync
        (discontinued) and is not used by Box Drive. Example: 'synced'.
            can_non_owners_invite (boolean): Specifies if users who are not the owner
        of the folder can invite new collaborators to the folder. Example: 'True'.
            parent (string): parent
            shared_link (string): shared_link
            folder_upload_email (string): folder_upload_email
            tags (array): The tags for this item. These tags are shown in
        the Box web app and mobile apps next to an item.

        To add or remove a tag, retrieve the item's current tags,
        modify them, and then update this field.

        There is a limit of 100 tags per item, and 10,000
        unique tags per enterprise. Example: "['approved']".
            is_collaboration_restricted_to_enterprise (boolean): Specifies if new invites to this folder are restricted to users
        within the enterprise. This does not affect existing
        collaborations. Example: 'True'.
            collections (array): An array of collections to make this folder
        a member of. Currently
        we only support the `favorites` collection.

        To get the ID for a collection, use the
        [List all collections][1] endpoint.

        Passing an empty array `[]` or `null` will remove
        the folder from all collections.

        [1]: e://get-collections
            can_non_owners_view_collaborators (boolean): Restricts collaborators who are not the owner of
        this folder from viewing other collaborations on
        this folder.

        It also restricts non-owners from inviting new
        collaborators.

        When setting this field to `false`, it is required
        to also set `can_non_owners_invite_collaborators` to
        `false` if it has not already been set. Example: 'True'.

        Returns:
            dict[str, Any]: Returns a folder object for the updated folder

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        This call will return synchronously. This holds true even when
        moving folders with a large a large number of items in all of its
        descendants. For very large folders, this means the call could
        take minutes or hours to return.

        Tags:
            Folders, important
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        request_body = {
            'name': name,
            'description': description,
            'sync_state': sync_state,
            'can_non_owners_invite': can_non_owners_invite,
            'parent': parent,
            'shared_link': shared_link,
            'folder_upload_email': folder_upload_email,
            'tags': tags,
            'is_collaboration_restricted_to_enterprise': is_collaboration_restricted_to_enterprise,
            'collections': collections,
            'can_non_owners_view_collaborators': can_non_owners_view_collaborators,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folder_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_folders_id(self, folder_id, recursive=None) -> Any:
        """
        Deletes a folder with the specified ID, optionally removing all its contents recursively, and returns a status code indicating the success or failure of the operation.

        Args:
            folder_id (string): folder_id
            recursive (boolean): Delete a folder that is not empty by recursively deleting the
        folder and all of its content. Example: 'True'.

        Returns:
            Any: Returns an empty response when the folder is successfully deleted
        or moved to the trash.

        Tags:
            Folders
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}"
        query_params = {k: v for k, v in [('recursive', recursive)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_app_item_associations(self, folder_id, limit=None, marker=None, application_type=None) -> dict[str, Any]:
        """
        Retrieves a list of application item associations for a specified folder using the "GET" method, allowing optional filtering by limit, marker, and application type.

        Args:
            folder_id (string): folder_id
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            application_type (string): If given, returns only app items for this application type Example: 'hubs'.

        Returns:
            dict[str, Any]: Returns a collection of app item objects. If there are no
        app items on this folder an empty collection will be returned.
        This list includes app items on ancestors of this folder.

        Tags:
            App item associations
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/app_item_associations"
        query_params = {k: v for k, v in [('limit', limit), ('marker', marker), ('application_type', application_type)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_items(self, folder_id, fields=None, usemarker=None, marker=None, offset=None, limit=None, sort=None, direction=None) -> dict[str, Any]:
        """
        Retrieves a list of items within a specified Box folder using the "GET" method, returning files, folders, and web links based on the provided folder ID and optional query parameters for filtering and sorting.

        Args:
            folder_id (string): folder_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Additionally this field can be used to query any metadata
        applied to the file by specifying the `metadata` field as well
        as the scope and key of the template to retrieve, for example
        `?fields=metadata.enterprise_12345.contractTemplate`. Example: "['id', 'type', 'name']".
            usemarker (boolean): Specifies whether to use marker-based pagination instead of
        offset-based pagination. Only one pagination method can
        be used at a time. By setting this value to true, the API will return a `marker` field
        that can be passed as a parameter to this endpoint to get the next
        page of the response. Example: 'True'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            sort (string): Defines the **second** attribute by which items
        are sorted. The folder type affects the way the items
        are sorted: * **Standard folder**: Items are always sorted by their `type` first, with folders listed before files, and files listed before web links. * **Root folder**: This parameter is not supported for marker-based pagination on the root folder (the folder with an `id` of `0`). * **Shared folder with parent path to the associated folder visible to the collaborator**: Items are always sorted by their `type` first, with folders listed before files, and files listed before web links. Example: 'id'.
            direction (string): The direction to sort results in. This can be either in alphabetical ascending
        (`ASC`) or descending (`DESC`) order. Example: 'ASC'.

        Returns:
            dict[str, Any]: Returns a collection of files, folders, and web links contained in a folder.

        Tags:
            Folders, important
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/items"
        query_params = {k: v for k, v in [('fields', fields), ('usemarker', usemarker), ('marker', marker), ('offset', offset), ('limit', limit), ('sort', sort), ('direction', direction)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folders(self, fields=None, name=None, parent=None, folder_upload_email=None, sync_state=None) -> dict[str, Any]:
        """
        Creates a new folder using the POST method at the "/folders" path, allowing for optional specification of fields to include in the response.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): The name for the new folder.

        There are some restrictions to the file name. Names containing
        non-printable ASCII characters, forward and backward slashes
        (`/`, `\`), as well as names with trailing spaces are
        prohibited.

        Additionally, the names `.` and `..` are
        not allowed either. Example: 'New Folder'.
            parent (object): The parent folder to create the new folder within.
            folder_upload_email (string): folder_upload_email
            sync_state (string): Specifies whether a folder should be synced to a
        user's device or not. This is used by Box Sync
        (discontinued) and is not used by Box Drive. Example: 'synced'.

        Returns:
            dict[str, Any]: Returns a folder object.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        Tags:
            Folders, important
        """
        request_body = {
            'name': name,
            'parent': parent,
            'folder_upload_email': folder_upload_email,
            'sync_state': sync_state,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folders_id_copy(self, folder_id, fields=None, name=None, parent=None) -> dict[str, Any]:
        """
        Copies a specified folder with the given `folder_id` to a destination folder, creating a duplicate of the original folder's contents.

        Args:
            folder_id (string): folder_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): An optional new name for the copied folder.

        There are some restrictions to the file name. Names containing
        non-printable ASCII characters, forward and backward slashes
        (`/`, `\`), as well as names with trailing spaces are
        prohibited.

        Additionally, the names `.` and `..` are
        not allowed either. Example: 'New Folder'.
            parent (object): The destination folder to copy the folder to.

        Returns:
            dict[str, Any]: Returns a new folder object representing the copied folder.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        Tags:
            Folders
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        request_body = {
            'name': name,
            'parent': parent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folder_id}/copy"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_collaborations(self, folder_id, fields=None, limit=None, marker=None) -> dict[str, Any]:
        """
        Retrieves a list of pending and active collaborations for a specified folder, returning all users who have access or have been invited to the folder[1][3][4].

        Args:
            folder_id (string): folder_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.

        Returns:
            dict[str, Any]: Returns a collection of collaboration objects. If there are no
        collaborations on this folder an empty collection will be returned.

        This list includes pending collaborations, for which the `status`
        is set to `pending`, indicating invitations that have been sent but not
        yet accepted.

        Tags:
            Collaborations (List)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/collaborations"
        query_params = {k: v for k, v in [('fields', fields), ('limit', limit), ('marker', marker)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_trash(self, folder_id, fields=None) -> dict[str, Any]:
        """
        Retrieves the details of a specified folder that has been moved to the trash, including information about when it was trashed.

        Args:
            folder_id (string): folder_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the folder that was trashed,
        including information about when the it
        was moved to the trash.

        Tags:
            Trashed folders
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/trash"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_folders_id_trash(self, folder_id) -> Any:
        """
        Permanently deletes a folder (and its contents) from the trash, or if not already in the trash, moves the specified folder to the trash for eventual deletion.

        Args:
            folder_id (string): folder_id

        Returns:
            Any: Returns an empty response when the folder was
        permanently deleted.

        Tags:
            Trashed folders
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/trash"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_metadata(self, folder_id) -> dict[str, Any]:
        """
        Retrieves metadata for a specific folder identified by its ID using the GET method.

        Args:
            folder_id (string): folder_id

        Returns:
            dict[str, Any]: Returns all the metadata associated with a folder.

        This API does not support pagination and will therefore always return
        all of the metadata associated to the folder.

        Tags:
            Metadata instances (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/metadata"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo(self, folder_id) -> dict[str, Any]:
        """
        Retrieves the classification metadata instance applied to a specified folder, which includes security classifications set for the folder using the enterprise security classification template.

        Args:
            folder_id (string): folder_id

        Returns:
            dict[str, Any]: Returns an instance of the `securityClassification` metadata
        template, which contains a `Box__Security__Classification__Key`
        field that lists all the classifications available to this
        enterprise.

        Tags:
            Classifications on folders
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo(self, folder_id, Box__Security__Classification__Key=None) -> dict[str, Any]:
        """
        Adds a security classification to a folder using the provided `folder_id` by specifying the classification label, utilizing the Box API.

        Args:
            folder_id (string): folder_id
            Box__Security__Classification__Key (string): The name of the classification to apply to this folder.

        To list the available classifications in an enterprise,
        use the classification API to retrieve the
        [classification template](e://get_metadata_templates_enterprise_securityClassification-6VMVochwUWo_schema)
        which lists all available classification keys. Example: 'Sensitive'.

        Returns:
            dict[str, Any]: Returns the classification template instance
        that was applied to the folder.

        Tags:
            Classifications on folders
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        request_body = {
            'Box__Security__Classification__Key': Box__Security__Classification__Key,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()


    def delete_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo(self, folder_id) -> Any:
        """
        Removes any security classifications from a specified folder using the Box Platform API.

        Args:
            folder_id (string): folder_id

        Returns:
            Any: Returns an empty response when the classification is
        successfully deleted.

        Tags:
            Classifications on folders
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_metadata_id_id(self, folder_id, scope, template_key) -> dict[str, Any]:
        """
        Retrieves metadata for a specific folder according to the specified scope and template key.

        Args:
            folder_id (string): folder_id
            scope (string): scope
            template_key (string): template_key

        Returns:
            dict[str, Any]: An instance of the metadata template that includes
        additional "key:value" pairs defined by the user or
        an application.

        Tags:
            Metadata instances (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        if scope is None:
            raise ValueError("Missing required parameter 'scope'")
        if template_key is None:
            raise ValueError("Missing required parameter 'template_key'")
        url = f"{self.base_url}/folders/{folder_id}/metadata/{scope}/{template_key}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()


    def delete_folders_id_metadata_id_id(self, folder_id, scope, template_key) -> Any:
        """
        Deletes a metadata template instance from a specified folder using the provided folder ID, scope, and template key.

        Args:
            folder_id (string): folder_id
            scope (string): scope
            template_key (string): template_key

        Returns:
            Any: Returns an empty response when the metadata is
        successfully deleted.

        Tags:
            Metadata instances (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        if scope is None:
            raise ValueError("Missing required parameter 'scope'")
        if template_key is None:
            raise ValueError("Missing required parameter 'template_key'")
        url = f"{self.base_url}/folders/{folder_id}/metadata/{scope}/{template_key}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_trash_items(self, fields=None, limit=None, offset=None, usemarker=None, marker=None, direction=None, sort=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of items currently residing in the trash folder, supporting optional filtering, sorting, and field selection.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            usemarker (boolean): Specifies whether to use marker-based pagination instead of
        offset-based pagination. Only one pagination method can
        be used at a time. By setting this value to true, the API will return a `marker` field
        that can be passed as a parameter to this endpoint to get the next
        page of the response. Example: 'True'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            direction (string): The direction to sort results in. This can be either in alphabetical ascending
        (`ASC`) or descending (`DESC`) order. Example: 'ASC'.
            sort (string): Defines the **second** attribute by which items
        are sorted. Items are always sorted by their `type` first, with
        folders listed before files, and files listed
        before web links. This parameter is not supported when using marker-based pagination. Example: 'name'.

        Returns:
            dict[str, Any]: Returns a list of items that have been deleted

        Tags:
            Trashed items
        """
        url = f"{self.base_url}/folders/trash/items"
        query_params = {k: v for k, v in [('fields', fields), ('limit', limit), ('offset', offset), ('usemarker', usemarker), ('marker', marker), ('direction', direction), ('sort', sort)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_watermark(self, folder_id) -> dict[str, Any]:
        """
        Retrieves the watermark information for a specific folder using the folder ID.

        Args:
            folder_id (string): folder_id

        Returns:
            dict[str, Any]: Returns an object containing information about the
        watermark associated for to this folder.

        Tags:
            Watermarks (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/watermark"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_folders_id_watermark(self, folder_id, watermark=None) -> dict[str, Any]:
        """
        Applies a watermark to a specified folder using the Box API by sending a PUT request to the "/folders/{folder_id}/watermark" endpoint.

        Args:
            folder_id (string): folder_id
            watermark (object): The watermark to imprint on the folder

        Returns:
            dict[str, Any]: Returns an updated watermark if a watermark already
        existed on this folder.

        Tags:
            Watermarks (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        request_body = {
            'watermark': watermark,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folder_id}/watermark"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_folders_id_watermark(self, folder_id) -> Any:
        """
        Deletes a watermark from a specified folder by its ID using the Box API.

        Args:
            folder_id (string): folder_id

        Returns:
            Any: An empty response will be returned when the watermark
        was successfully deleted.

        Tags:
            Watermarks (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}/watermark"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folder_locks(self, folder_id) -> dict[str, Any]:
        """
        Retrieves information about folder locks for a specified folder using its ID.

        Args:
            folder_id (string): The unique identifier that represent a folder. The ID for any folder can be determined
        by visiting this folder in the web application
        and copying the ID from the URL. For example,
        for the URL `
        the `folder_id` is `123`. The root folder of a Box account is
        always represented by the ID `0`. Example: '12345'.

        Returns:
            dict[str, Any]: Returns details for all folder locks applied to the folder, including the
        lock type and user that applied the lock.

        Tags:
            Folder Locks
        """
        url = f"{self.base_url}/folder_locks"
        query_params = {k: v for k, v in [('folder_id', folder_id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folder_locks(self, locked_operations=None, folder=None) -> dict[str, Any]:
        """
        Creates a lock on a specified folder to prevent users from performing certain actions such as moving, deleting, or renaming the folder.

        Args:
            locked_operations (object): The operations to lock for the folder. If `locked_operations` is
        included in the request, both `move` and `delete` must also be
        included and both set to `true`.
            folder (object): The folder to apply the lock to.

        Returns:
            dict[str, Any]: Returns the instance of the folder lock that was applied to the folder,
        including the user that applied the lock and the operations set.

        Tags:
            Folder Locks
        """
        request_body = {
            'locked_operations': locked_operations,
            'folder': folder,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folder_locks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_folder_locks_id(self, folder_lock_id) -> Any:
        """
        Deletes a folder lock with the specified `folder_lock_id` in Box, requiring authentication as the folder's owner or co-owner.

        Args:
            folder_lock_id (string): folder_lock_id

        Returns:
            Any: Returns an empty response when the folder lock is successfully deleted.

        Tags:
            Folder Locks
        """
        if folder_lock_id is None:
            raise ValueError("Missing required parameter 'folder_lock_id'")
        url = f"{self.base_url}/folder_locks/{folder_lock_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_metadata_templates(self, metadata_instance_id, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of metadata templates, optionally filtered by a specific metadata instance ID, marker, and limit, using the GET method at the "/metadata_templates" path.

        Args:
            metadata_instance_id (string): The ID of an instance of the metadata template to find. Example: '01234500-12f1-1234-aa12-b1d234cb567e'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a list containing the 1 metadata template that matches the
        instance ID.

        Tags:
            Metadata templates
        """
        url = f"{self.base_url}/metadata_templates"
        query_params = {k: v for k, v in [('metadata_instance_id', metadata_instance_id), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_metadata_templates_enterprise_security_classification_6_vmvochw_uwo_schema(self) -> dict[str, Any]:
        """
        Retrieves the security classification metadata template schema, listing all available classification labels and their details for the enterprise.

        Returns:
            dict[str, Any]: Returns the `securityClassification` metadata template, which contains
        a `Box__Security__Classification__Key` field that lists all the
        classifications available to this enterprise.

        Tags:
            Classifications
        """
        url = f"{self.base_url}/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_metadata_templates_enterprise_security_classification_6_vmvochw_uwo_schema_add(self, items=None) -> dict[str, Any]:
        """
        Updates the labels and descriptions of one or more security classifications available to an enterprise using the Box API.

        Args:

        Returns:
            dict[str, Any]: Returns the updated `securityClassification` metadata template, which
        contains a `Box__Security__Classification__Key` field that lists all
        the classifications available to this enterprise.

        Tags:
            Classifications
        """
        # Use items array directly as request body
        request_body = items
        url = f"{self.base_url}/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema#add"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()


    def get_metadata_templates_id_id_schema(self, scope, template_key) -> dict[str, Any]:
        """
        Retrieves the schema for a specific metadata template defined by the scope and template key using the "GET" method.

        Args:
            scope (string): scope
            template_key (string): template_key

        Returns:
            dict[str, Any]: Returns the metadata template matching the `scope`
        and `template` name.

        Tags:
            Metadata templates
        """
        if scope is None:
            raise ValueError("Missing required parameter 'scope'")
        if template_key is None:
            raise ValueError("Missing required parameter 'template_key'")
        url = f"{self.base_url}/metadata_templates/{scope}/{template_key}/schema"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()


    def delete_metadata_templates_id_id_schema(self, scope, template_key) -> Any:
        """
        Deletes a metadata template and its associated instances within a specified scope using the provided template key, returning a 204 No Content response upon successful removal.

        Args:
            scope (string): scope
            template_key (string): template_key

        Returns:
            Any: Returns an empty response when the metadata
        template is successfully deleted.

        Tags:
            Metadata templates
        """
        if scope is None:
            raise ValueError("Missing required parameter 'scope'")
        if template_key is None:
            raise ValueError("Missing required parameter 'template_key'")
        url = f"{self.base_url}/metadata_templates/{scope}/{template_key}/schema"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_metadata_templates_id(self, template_id) -> dict[str, Any]:
        """
        Retrieves specific details of a metadata template by its ID using the GET method at the "/metadata_templates/{template_id}" endpoint.

        Args:
            template_id (string): template_id

        Returns:
            dict[str, Any]: Returns the metadata template that matches the ID.

        Tags:
            Metadata templates
        """
        if template_id is None:
            raise ValueError("Missing required parameter 'template_id'")
        url = f"{self.base_url}/metadata_templates/{template_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_metadata_templates_global(self, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of all global metadata templates available to everyone using Box, regardless of their enterprise.

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns all of the metadata templates available to all enterprises
        and their corresponding schema.

        Tags:
            Metadata templates
        """
        url = f"{self.base_url}/metadata_templates/global"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_metadata_templates_enterprise(self, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of metadata templates for an enterprise using the Box API, allowing users to manage and access custom templates created within their organization.

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns all of the metadata templates within an enterprise
        and their corresponding schema.

        Tags:
            Metadata templates
        """
        url = f"{self.base_url}/metadata_templates/enterprise"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_metadata_templates_schema(self, scope=None, templateKey=None, displayName=None, hidden=None, fields=None, copyInstanceOnItemCopy=None) -> dict[str, Any]:
        """
        Creates a metadata template by passing a scope, display name, and optional fields to define the structure of metadata, returning a created template upon successful execution.

        Args:
            scope (string): The scope of the metadata template to create. Applications can
        only create templates for use within the authenticated user's
        enterprise.

        This value needs to be set to `enterprise`, as `global` scopes can
        not be created by applications. Example: 'enterprise'.
            templateKey (string): A unique identifier for the template. This identifier needs to be
        unique across the enterprise for which the metadata template is
        being created.

        When not provided, the API will create a unique `templateKey`
        based on the value of the `displayName`. Example: 'productInfo'.
            displayName (string): The display name of the template. Example: 'Product Info'.
            hidden (boolean): Defines if this template is visible in the Box web app UI, or if
        it is purely intended for usage through the API. Example: 'True'.
            fields (array): An ordered list of template fields which are part of the template.
        Each field can be a regular text field, date field, number field,
        as well as a single or multi-select list.
            copyInstanceOnItemCopy (boolean): Whether or not to copy any metadata attached to a file or folder
        when it is copied. By default, metadata is not copied along with a
        file or folder when it is copied. Example: 'True'.

        Returns:
            dict[str, Any]: The schema representing the metadata template created.

        Tags:
            Metadata templates
        """
        request_body = {
            'scope': scope,
            'templateKey': templateKey,
            'displayName': displayName,
            'hidden': hidden,
            'fields': fields,
            'copyInstanceOnItemCopy': copyInstanceOnItemCopy,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/metadata_templates/schema"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_metadata_templates_schema_classifications(self, scope=None, templateKey=None, displayName=None, hidden=None, copyInstanceOnItemCopy=None, fields=None) -> dict[str, Any]:
        """
        Initializes the metadata template with a set of classifications at the specified path "/metadata_templates/schema#classifications" using the "POST" method.

        Args:
            scope (string): The scope in which to create the classifications. This should
        be `enterprise` or `enterprise_{id}` where `id` is the unique
        ID of the enterprise. Example: 'enterprise'.
            templateKey (string): Defines the list of metadata templates. Example: 'securityClassification-6VMVochwUWo'.
            displayName (string): The name of the
        template as shown in web and mobile interfaces. Example: 'Classification'.
            hidden (boolean): Determines if the classification template is
        hidden or available on web and mobile
        devices. Example: 'False'.
            copyInstanceOnItemCopy (boolean): Determines if classifications are
        copied along when the file or folder is
        copied. Example: 'False'.
            fields (array): The classification template requires exactly
        one field, which holds
        all the valid classification values.

        Returns:
            dict[str, Any]: Returns a new `securityClassification` metadata template, which
        contains a `Box__Security__Classification__Key` field that lists all
        the classifications available to this enterprise.

        Tags:
            Classifications
        """
        request_body = {
            'scope': scope,
            'templateKey': templateKey,
            'displayName': displayName,
            'hidden': hidden,
            'copyInstanceOnItemCopy': copyInstanceOnItemCopy,
            'fields': fields,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/metadata_templates/schema#classifications"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_metadata_cascade_policies(self, folder_id, owner_enterprise_id=None, marker=None, offset=None) -> dict[str, Any]:
        """
        Retrieves a list of metadata cascade policies for a specified folder, using parameters such as folder ID, owner enterprise ID, and pagination controls like marker and offset.

        Args:
            folder_id (string): Specifies which folder to return policies for. This can not be used on the
        root folder with ID `0`. Example: '31232'.
            owner_enterprise_id (string): The ID of the enterprise ID for which to find metadata
        cascade policies. If not specified, it defaults to the
        current enterprise. Example: '31232'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a list of metadata cascade policies

        Tags:
            Metadata cascade policies
        """
        url = f"{self.base_url}/metadata_cascade_policies"
        query_params = {k: v for k, v in [('folder_id', folder_id), ('owner_enterprise_id', owner_enterprise_id), ('marker', marker), ('offset', offset)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_metadata_cascade_policies(self, folder_id=None, scope=None, templateKey=None) -> dict[str, Any]:
        """
        Creates a metadata cascade policy using the POST method at the "/metadata_cascade_policies" path, which automatically applies a metadata template instance to all files and folders within a specified folder.

        Args:
            folder_id (string): The ID of the folder to apply the policy to. This folder will
        need to already have an instance of the targeted metadata
        template applied to it. Example: '1234567'.
            scope (string): The scope of the targeted metadata template. This template will
        need to already have an instance applied to the targeted folder. Example: 'enterprise'.
            templateKey (string): The key of the targeted metadata template. This template will
        need to already have an instance applied to the targeted folder.

        In many cases the template key is automatically derived
        of its display name, for example `Contract Template` would
        become `contractTemplate`. In some cases the creator of the
        template will have provided its own template key.

        Please [list the templates for an enterprise][list], or
        get all instances on a [file][file] or [folder][folder]
        to inspect a template's key.

        [list]: e://get-metadata-templates-enterprise
        [file]: e://get-files-id-metadata
        [folder]: e://get-folders-id-metadata Example: 'productInfo'.

        Returns:
            dict[str, Any]: Returns a new of metadata cascade policy

        Tags:
            Metadata cascade policies
        """
        request_body = {
            'folder_id': folder_id,
            'scope': scope,
            'templateKey': templateKey,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/metadata_cascade_policies"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_metadata_cascade_policies_id(self, metadata_cascade_policy_id) -> dict[str, Any]:
        """
        Retrieves the details of a specific metadata cascade policy, which describes how a metadata template instance is automatically applied to all files and folders within a targeted folder, using the provided policy ID. [1][2][4]

        Args:
            metadata_cascade_policy_id (string): metadata_cascade_policy_id

        Returns:
            dict[str, Any]: Returns a metadata cascade policy

        Tags:
            Metadata cascade policies
        """
        if metadata_cascade_policy_id is None:
            raise ValueError("Missing required parameter 'metadata_cascade_policy_id'")
        url = f"{self.base_url}/metadata_cascade_policies/{metadata_cascade_policy_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_metadata_cascade_policies_id(self, metadata_cascade_policy_id) -> Any:
        """
        Deletes a specified metadata cascade policy, which stops the automatic cascading of metadata from a folder to its contents.

        Args:
            metadata_cascade_policy_id (string): metadata_cascade_policy_id

        Returns:
            Any: Returns an empty response when the policy
        is successfully deleted.

        Tags:
            Metadata cascade policies
        """
        if metadata_cascade_policy_id is None:
            raise ValueError("Missing required parameter 'metadata_cascade_policy_id'")
        url = f"{self.base_url}/metadata_cascade_policies/{metadata_cascade_policy_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_metadata_cascade_policies_id_apply(self, metadata_cascade_policy_id, conflict_resolution=None) -> Any:
        """
        [LLM could not generate summary for POST /metadata_cascade_policies/{metadata_cascade_policy_id}/apply]

        Args:
            metadata_cascade_policy_id (string): metadata_cascade_policy_id
            conflict_resolution (string): Describes the desired behavior when dealing with the conflict
        where a metadata template already has an instance applied
        to a child.

        * `none` will preserve the existing value on the file
        * `overwrite` will force-apply the templates values over
          any existing values. Example: 'none'.

        Returns:
            Any: Returns an empty response when the API call was successful. The metadata
        cascade operation will be performed asynchronously.

        The API call will return directly, before the cascade operation
        is complete. There is currently no API to check for the status of this
        operation.

        Tags:
            Metadata cascade policies
        """
        if metadata_cascade_policy_id is None:
            raise ValueError("Missing required parameter 'metadata_cascade_policy_id'")
        request_body = {
            'conflict_resolution': conflict_resolution,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/metadata_cascade_policies/{metadata_cascade_policy_id}/apply"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_metadata_queries_execute_read(self, from_=None, query=None, query_params=None, ancestor_folder_id=None, order_by=None, limit=None, marker=None, fields=None) -> dict[str, Any]:
        """
        Executes a metadata query using SQL-like syntax to retrieve files and folders from Box based on specific metadata criteria via a POST request to the "/metadata_queries/execute_read" endpoint.

        Args:
            from_ (string): Specifies the template used in the query. Must be in the form
        `scope.templateKey`. Not all templates can be used in this field,
        most notably the built-in, Box-provided classification templates
        can not be used in a query. Example: 'enterprise_123456.someTemplate'.
            query (string): The query to perform. A query is a logical expression that is very similar
        to a SQL `SELECT` statement. Values in the search query can be turned into
        parameters specified in the `query_param` arguments list to prevent having
        to manually insert search values into the query string.

        For example, a value of `:amount` would represent the `amount` value in
        `query_params` object. Example: 'value >= :amount'.
            query_params (object): Set of arguments corresponding to the parameters specified in the
        `query`. The type of each parameter used in the `query_params` must match
        the type of the corresponding metadata template field. Example: "{'amount': '100'}".
            ancestor_folder_id (string): The ID of the folder that you are restricting the query to. A
        value of zero will return results from all folders you have access
        to. A non-zero value will only return results found in the folder
        corresponding to the ID or in any of its subfolders. Example: '0'.
            order_by (array): A list of template fields and directions to sort the metadata query
        results by.

        The ordering `direction` must be the same for each item in the array.
            limit (integer): A value between 0 and 100 that indicates the maximum number of results
        to return for a single request. This only specifies a maximum
        boundary and will not guarantee the minimum number of results
        returned. Example: '50'.
            marker (string): Marker to use for requesting the next page. Example: 'AAAAAmVYB1FWec8GH6yWu2nwmanfMh07IyYInaa7DZDYjgO1H4KoLW29vPlLY173OKsci6h6xGh61gG73gnaxoS+o0BbI1/h6le6cikjlupVhASwJ2Cj0tOD9wlnrUMHHw3/ISf+uuACzrOMhN6d5fYrbidPzS6MdhJOejuYlvsg4tcBYzjauP3+VU51p77HFAIuObnJT0ff'.
            fields (array): By default, this endpoint returns only the most basic info about the items for
        which the query matches. This attribute can be used to specify a list of
        additional attributes to return for any item, including its metadata.

        This attribute takes a list of item fields, metadata template identifiers,
        or metadata template field identifiers.

        For example:

        * `created_by` will add the details of the user who created the item to
        the response.
        * `metadata.<scope>.<templateKey>` will return the mini-representation
        of the metadata instance identified by the `scope` and `templateKey`.
        * `metadata.<scope>.<templateKey>.<field>` will return all the mini-representation
        of the metadata instance identified by the `scope` and `templateKey` plus
        the field specified by the `field` name. Multiple fields for the same
        `scope` and `templateKey` can be defined. Example: "['extension', 'created_at', 'item_status', 'metadata.enterprise_1234.contracts', 'metadata.enterprise_1234.regions.location']".

        Returns:
            dict[str, Any]: Returns a list of files and folders that match this metadata query.

        Tags:
            Search
        """
        request_body = {
            'from': from_,
            'query': query,
            'query_params': query_params,
            'ancestor_folder_id': ancestor_folder_id,
            'order_by': order_by,
            'limit': limit,
            'marker': marker,
            'fields': fields,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/metadata_queries/execute_read"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_comments_id(self, comment_id, fields=None) -> dict[str, Any]:
        """
        Retrieves details of a specific comment by its ID, optionally returning only specified fields.

        Args:
            comment_id (string): comment_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a full comment object.

        Tags:
            Comments
        """
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        url = f"{self.base_url}/comments/{comment_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_comments_id(self, comment_id, fields=None, message=None) -> dict[str, Any]:
        """
        Replaces or updates a comment with the specified comment_id using the provided data and returns a status indicating success or failure.

        Args:
            comment_id (string): comment_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            message (string): The text of the comment to update Example: 'Review completed!'.

        Returns:
            dict[str, Any]: Returns the updated comment object.

        Tags:
            Comments
        """
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        request_body = {
            'message': message,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/comments/{comment_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_comments_id(self, comment_id) -> Any:
        """
        Deletes a comment identified by its unique `comment_id` using the HTTP DELETE method.

        Args:
            comment_id (string): comment_id

        Returns:
            Any: Returns an empty response when the comment has been deleted.

        Tags:
            Comments
        """
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        url = f"{self.base_url}/comments/{comment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_comments(self, fields=None, message=None, tagged_message=None, item=None) -> dict[str, Any]:
        """
        Creates a new comment and allows specifying which fields to include in the response.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            message (string): The text of the comment.

        To mention a user, use the `tagged_message`
        parameter instead. Example: 'Review completed!'.
            tagged_message (string): The text of the comment, including `@[user_id:name]`
        somewhere in the message to mention another user, which
        will send them an email notification, letting them know
        they have been mentioned.

        The `user_id` is the target user's ID, where the `name`
        can be any custom phrase. In the Box UI this name will
        link to the user's profile.

        If you are not mentioning another user, use `message`
        instead. Example: '@[1234:John] Review completed!'.
            item (object): The item to attach the comment to.

        Returns:
            dict[str, Any]: Returns the newly created comment object.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields.

        Tags:
            Comments
        """
        request_body = {
            'message': message,
            'tagged_message': tagged_message,
            'item': item,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/comments"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collaborations_id(self, collaboration_id, fields=None) -> dict[str, Any]:
        """
        Retrieves details of a specific collaboration identified by its unique ID, optionally filtering the returned fields as specified in the request.

        Args:
            collaboration_id (string): collaboration_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a collaboration object.

        Tags:
            Collaborations
        """
        if collaboration_id is None:
            raise ValueError("Missing required parameter 'collaboration_id'")
        url = f"{self.base_url}/collaborations/{collaboration_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_collaborations_id(self, collaboration_id, role=None, status=None, expires_at=None, can_view_path=None) -> dict[str, Any]:
        """
        Updates a collaboration by replacing it with the data sent in the request body at the specified collaboration ID using the PUT method.

        Args:
            collaboration_id (string): collaboration_id
            role (string): The level of access granted. Example: 'editor'.
            status (string): <!--alex ignore reject-->
        Set the status of a `pending` collaboration invitation,
        effectively accepting, or rejecting the invite. Example: 'accepted'.
            expires_at (string): Update the expiration date for the collaboration. At this date,
        the collaboration will be automatically removed from the item.

        This feature will only work if the **Automatically remove invited
        collaborators: Allow folder owners to extend the expiry date**
        setting has been enabled in the **Enterprise Settings**
        of the **Admin Console**. When the setting is not enabled,
        collaborations can not have an expiry date and a value for this
        field will be result in an error.

        Additionally, a collaboration can only be given an
        expiration if it was created after the **Automatically remove
        invited collaborator** setting was enabled. Example: '2019-08-29T23:59:00-07:00'.
            can_view_path (boolean): Determines if the invited users can see the entire parent path to
        the associated folder. The user will not gain privileges in any
        parent folder and therefore can not see content the user is not
        collaborated on.

        Be aware that this meaningfully increases the time required to load the
        invitee's **All Files** page. We recommend you limit the number of
        collaborations with `can_view_path` enabled to 1,000 per user.

        Only owner or co-owners can invite collaborators with a `can_view_path` of
        `true`.

        `can_view_path` can only be used for folder collaborations. Example: 'True'.

        Returns:
            dict[str, Any]: Returns an updated collaboration object unless the owner has changed.

        Tags:
            Collaborations
        """
        if collaboration_id is None:
            raise ValueError("Missing required parameter 'collaboration_id'")
        request_body = {
            'role': role,
            'status': status,
            'expires_at': expires_at,
            'can_view_path': can_view_path,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/collaborations/{collaboration_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_collaborations_id(self, collaboration_id) -> Any:
        """
        Deletes a collaboration specified by the `collaboration_id` using the DELETE method, returning an HTTP 204 response if successful.

        Args:
            collaboration_id (string): collaboration_id

        Returns:
            Any: A blank response is returned if the collaboration was
        successfully deleted.

        Tags:
            Collaborations
        """
        if collaboration_id is None:
            raise ValueError("Missing required parameter 'collaboration_id'")
        url = f"{self.base_url}/collaborations/{collaboration_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collaborations(self, status, fields=None, offset=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of collaborations filtered by status, with optional fields and pagination, using the GET method at the "/collaborations" endpoint.

        Args:
            status (string): The status of the collaborations to retrieve Example: 'pending'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of pending collaboration objects.

        If the user has no pending collaborations, the collection
        will be empty.

        Tags:
            Collaborations (List)
        """
        url = f"{self.base_url}/collaborations"
        query_params = {k: v for k, v in [('status', status), ('fields', fields), ('offset', offset), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_collaborations(self, fields=None, notify=None, item=None, accessible_by=None, role=None, is_access_only=None, can_view_path=None, expires_at=None) -> dict[str, Any]:
        """
        Creates new collaborations using the POST method at the "/collaborations" path, allowing optional query parameters for specifying fields and notifications.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            notify (boolean): Determines if users should receive email notification
        for the action performed. Example: 'True'.
            item (object): The item to attach the comment to.
            accessible_by (object): The user or group to give access to the item.
            role (string): The level of access granted. Example: 'editor'.
            is_access_only (boolean): If set to `true`, collaborators have access to
        shared items, but such items won't be visible in the
        All Files list. Additionally, collaborators won't
        see the the path to the root folder for the
        shared item. Example: 'True'.
            can_view_path (boolean): Determines if the invited users can see the entire parent path to
        the associated folder. The user will not gain privileges in any
        parent folder and therefore can not see content the user is not
        collaborated on.

        Be aware that this meaningfully increases the time required to load the
        invitee's **All Files** page. We recommend you limit the number of
        collaborations with `can_view_path` enabled to 1,000 per user.

        Only owner or co-owners can invite collaborators with a `can_view_path` of
        `true`.

        `can_view_path` can only be used for folder collaborations. Example: 'True'.
            expires_at (string): Set the expiration date for the collaboration. At this date, the
        collaboration will be automatically removed from the item.

        This feature will only work if the **Automatically remove invited
        collaborators: Allow folder owners to extend the expiry date**
        setting has been enabled in the **Enterprise Settings**
        of the **Admin Console**. When the setting is not enabled,
        collaborations can not have an expiry date and a value for this
        field will be result in an error. Example: '2019-08-29T23:59:00-07:00'.

        Returns:
            dict[str, Any]: Returns a new collaboration object.

        Tags:
            Collaborations
        """
        request_body = {
            'item': item,
            'accessible_by': accessible_by,
            'role': role,
            'is_access_only': is_access_only,
            'can_view_path': can_view_path,
            'expires_at': expires_at,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/collaborations"
        query_params = {k: v for k, v in [('fields', fields), ('notify', notify)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_search(self, query=None, scope=None, file_extensions=None, created_at_range=None, updated_at_range=None, size_range=None, owner_user_ids=None, recent_updater_user_ids=None, ancestor_folder_ids=None, content_types=None, type=None, trash_content=None, mdfilters=None, sort=None, direction=None, limit=None, include_recent_shared_links=None, fields=None, offset=None, deleted_user_ids=None, deleted_at_range=None) -> Any:
        """
        Searches GitHub resources using the "GET" method at the "/search" path, allowing for filtering by various parameters such as query, scope, file extensions, creation and update times, size range, and more to return relevant results.

        Args:
            query (string): The string to search for. This query is matched against item names,
        descriptions, text content of files, and various other fields of
        the different item types. This parameter supports a variety of operators to further refine
        the results returns. * `""` - by wrapping a query in double quotes only exact matches are returned by the API. Exact searches do not return search matches based on specific character sequences. Instead, they return matches based on phrases, that is, word sequences. For example: A search for `"Blue-Box"` may return search results including the sequence `"blue.box"`, `"Blue Box"`, and `"Blue-Box"`; any item containing the words `Blue` and `Box` consecutively, in the order specified.
        * `AND` - returns items that contain both the search terms. For example, a search for `marketing AND BoxWorks` returns items that have both `marketing` and `BoxWorks` within its text in any order. It does not return a result that only has `BoxWorks` in its text.
        * `OR` - returns items that contain either of the search terms. For example, a search for `marketing OR BoxWorks` returns a result that has either `marketing` or `BoxWorks` within its text. Using this operator is not necessary as we implicitly interpret multi-word queries as `OR` unless another supported boolean term is used.
        * `NOT` - returns items that do not contain the search term provided. For example, a search for `marketing AND NOT BoxWorks` returns a result that has only `marketing` within its text. Results containing `BoxWorks` are omitted. We do not support lower case (that is,
        `and`, `or`, and `not`) or mixed case (that is, `And`, `Or`, and `Not`)
        operators. This field is required unless the `mdfilters` parameter is defined. Example: 'sales'.
            scope (string): Limits the search results to either the files that the user has
        access to, or to files available to the entire enterprise. The scope defaults to `user_content`, which limits the search
        results to content that is available to the currently authenticated
        user. The `enterprise_content` can be requested by an admin through our
        support channels. Once this scope has been enabled for a user, it
        will allow that use to query for content across the entire
        enterprise and not only the content that they have access to. Example: 'user_content'.
            file_extensions (array): Limits the search results to any files that match any of the provided
        file extensions. This list is a comma-separated list of file extensions
        without the dots. Example: "['pdf', 'png', 'gif']".
            created_at_range (array): Limits the search results to any items created within
        a given date range. Date ranges are defined as comma separated RFC3339
        timestamps. If the the start date is omitted (`,2014-05-17T13:35:01-07:00`)
        anything created before the end date will be returned. If the end date is omitted (`2014-05-15T13:35:01-07:00,`) the
        current date will be used as the end date instead. Example: "['2014-05-15T13:35:01-07:00', '2014-05-17T13:35:01-07:00']".
            updated_at_range (array): Limits the search results to any items updated within
        a given date range. Date ranges are defined as comma separated RFC3339
        timestamps. If the start date is omitted (`,2014-05-17T13:35:01-07:00`)
        anything updated before the end date will be returned. If the end date is omitted (`2014-05-15T13:35:01-07:00,`) the
        current date will be used as the end date instead. Example: "['2014-05-15T13:35:01-07:00', '2014-05-17T13:35:01-07:00']".
            size_range (array): Limits the search results to any items with a size within
        a given file size range. This applied to files and folders. Size ranges are defined as comma separated list of a lower
        and upper byte size limit (inclusive). The upper and lower bound can be omitted to create open ranges. Example: '[1000000, 5000000]'.
            owner_user_ids (array): Limits the search results to any items that are owned
        by the given list of owners, defined as a list of comma separated
        user IDs. The items still need to be owned or shared with
        the currently authenticated user for them to show up in the search
        results. If the user does not have access to any files owned by any of
        the users an empty result set will be returned. To search across an entire enterprise, we recommend using the
        `enterprise_content` scope parameter which can be requested with our
        support team. Example: "['123422', '23532', '3241212']".
            recent_updater_user_ids (array): Limits the search results to any items that have been updated
        by the given list of users, defined as a list of comma separated
        user IDs. The items still need to be owned or shared with
        the currently authenticated user for them to show up in the search
        results. If the user does not have access to any files owned by any of
        the users an empty result set will be returned. This feature only searches back to the last 10 versions of an item. Example: "['123422', '23532', '3241212']".
            ancestor_folder_ids (array): Limits the search results to items within the given
        list of folders, defined as a comma separated lists
        of folder IDs. Search results will also include items within any subfolders
        of those ancestor folders. The folders still need to be owned or shared with
        the currently authenticated user. If the folder is not accessible by this
        user, or it does not exist, a `HTTP 404` error code will be returned
        instead. To search across an entire enterprise, we recommend using the
        `enterprise_content` scope parameter which can be requested with our
        support team. Example: "['4535234', '234123235', '2654345']".
            content_types (array): Limits the search results to any items that match the search query
        for a specific part of the file, for example the file description. Content types are defined as a comma separated lists
        of Box recognized content types. The allowed content types are as follows. * `name` - The name of the item, as defined by its `name` field.
        * `description` - The description of the item, as defined by its `description` field.
        * `file_content` - The actual content of the file.
        * `comments` - The content of any of the comments on a file or folder.
        * `tags` - Any tags that are applied to an item, as defined by its `tags` field. Example: "['name', 'description']".
            type (string): Limits the search results to any items of this type. This
        parameter only takes one value. By default the API returns
        items that match any of these types. * `file` - Limits the search results to files
        * `folder` - Limits the search results to folders
        * `web_link` - Limits the search results to web links, also known as bookmarks Example: 'file'.
            trash_content (string): Determines if the search should look in the trash for items. By default, this API only returns search results for items
        not currently in the trash (`non_trashed_only`). * `trashed_only` - Only searches for items currently in the trash
        * `non_trashed_only` - Only searches for items currently not in the trash
        * `all_items` - Searches for both trashed and non-trashed items. Example: 'non_trashed_only'.
            mdfilters (array): Limits the search results to any items for which the metadata matches the provided filter.
        This parameter is a list that specifies exactly **one** metadata template used to filter the search results. The parameter is required unless the `query` parameter is provided. Example: "[{'scope': 'enterprise', 'templateKey': 'contract', 'filters': [{'category': 'online'}, {'contractValue': 100000}]}]".
            sort (string): Defines the order in which search results are returned. This API
        defaults to returning items by relevance unless this parameter is
        explicitly specified. * `relevance` (default) returns the results sorted by relevance to the
        query search term. The relevance is based on the occurrence of the search
        term in the items name, description, content, and additional properties.
        * `modified_at` returns the results ordered in descending order by date
        at which the item was last modified. Example: 'modified_at'.
            direction (string): Defines the direction in which search results are ordered. This API
        defaults to returning items in descending (`DESC`) order unless this
        parameter is explicitly specified. When results are sorted by `relevance` the ordering is locked to returning
        items in descending order of relevance, and this parameter is ignored. Example: 'ASC'.
            limit (integer): Defines the maximum number of items to return as part of a page of
        results. Example: '100'.
            include_recent_shared_links (boolean): Defines whether the search results should include any items
        that the user recently accessed through a shared link. When this parameter has been set to true,
        the format of the response of this API changes to return
        a list of [Search Results with
        Shared Links](r://search_results_with_shared_links) Example: 'True'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            deleted_user_ids (array): Limits the search results to items that were deleted by the given
        list of users, defined as a list of comma separated user IDs. The `trash_content` parameter needs to be set to `trashed_only`. If searching in trash is not performed, an empty result set
        is returned. The items need to be owned or shared with
        the currently authenticated user for them to show up in the search
        results. If the user does not have access to any files owned by
        any of the users, an empty result set is returned. Data available from 2023-02-01 onwards. Example: "['123422', '23532', '3241212']".
            deleted_at_range (array): Limits the search results to any items deleted within a given
        date range. Date ranges are defined as comma separated RFC3339 timestamps. If the the start date is omitted (`2014-05-17T13:35:01-07:00`),
        anything deleted before the end date will be returned. If the end date is omitted (`2014-05-15T13:35:01-07:00`),
        the current date will be used as the end date instead. The `trash_content` parameter needs to be set to `trashed_only`. If searching in trash is not performed, then an empty result
        is returned. Data available from 2023-02-01 onwards. Example: "['2014-05-15T13:35:01-07:00', '2014-05-17T13:35:01-07:00']".

        Returns:
            Any: Returns a collection of search results. If there are no matching
        search results, the `entries` array will be empty.

        Tags:
            Search
        """
        url = f"{self.base_url}/search"
        query_params = {k: v for k, v in [('query', query), ('scope', scope), ('file_extensions', file_extensions), ('created_at_range', created_at_range), ('updated_at_range', updated_at_range), ('size_range', size_range), ('owner_user_ids', owner_user_ids), ('recent_updater_user_ids', recent_updater_user_ids), ('ancestor_folder_ids', ancestor_folder_ids), ('content_types', content_types), ('type', type), ('trash_content', trash_content), ('mdfilters', mdfilters), ('sort', sort), ('direction', direction), ('limit', limit), ('include_recent_shared_links', include_recent_shared_links), ('fields', fields), ('offset', offset), ('deleted_user_ids', deleted_user_ids), ('deleted_at_range', deleted_at_range)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_tasks(self, item=None, action=None, message=None, due_at=None, completion_rule=None) -> dict[str, Any]:
        """
        Creates a new task and returns relevant details about the created task.

        Args:
            item (object): The file to attach the task to.
            action (string): The action the task assignee will be prompted to do. Must be

        * `review` defines an approval task that can be approved or
        rejected
        * `complete` defines a general task which can be completed Example: 'review'.
            message (string): An optional message to include with the task. Example: 'Please review'.
            due_at (string): Defines when the task is due. Defaults to `null` if not
        provided. Example: '2012-12-12T10:53:43-08:00'.
            completion_rule (string): Defines which assignees need to complete this task before the task
        is considered completed.

        * `all_assignees` (default) requires all assignees to review or
        approve the the task in order for it to be considered completed.
        * `any_assignee` accepts any one assignee to review or
        approve the the task in order for it to be considered completed. Example: 'all_assignees'.

        Returns:
            dict[str, Any]: Returns the newly created task.

        Tags:
            Tasks
        """
        request_body = {
            'item': item,
            'action': action,
            'message': message,
            'due_at': due_at,
            'completion_rule': completion_rule,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/tasks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_tasks_id(self, task_id) -> dict[str, Any]:
        """
        Retrieves a specific task identified by `{task_id}` using the GET method from the path "/tasks/{task_id}".

        Args:
            task_id (string): task_id

        Returns:
            dict[str, Any]: Returns a task object.

        Tags:
            Tasks
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/tasks/{task_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_tasks_id(self, task_id, action=None, message=None, due_at=None, completion_rule=None) -> dict[str, Any]:
        """
        Replaces or updates an existing task with the provided data for the specified task_id.

        Args:
            task_id (string): task_id
            action (string): The action the task assignee will be prompted to do. Must be

        * `review` defines an approval task that can be approved or
        rejected
        * `complete` defines a general task which can be completed Example: 'review'.
            message (string): The message included with the task. Example: 'Please review'.
            due_at (string): When the task is due at. Example: '2012-12-12T10:53:43-08:00'.
            completion_rule (string): Defines which assignees need to complete this task before the task
        is considered completed.

        * `all_assignees` (default) requires all assignees to review or
        approve the the task in order for it to be considered completed.
        * `any_assignee` accepts any one assignee to review or
        approve the the task in order for it to be considered completed. Example: 'all_assignees'.

        Returns:
            dict[str, Any]: Returns the updated task object

        Tags:
            Tasks
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        request_body = {
            'action': action,
            'message': message,
            'due_at': due_at,
            'completion_rule': completion_rule,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/tasks/{task_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_tasks_id(self, task_id) -> Any:
        """
        Deletes a task with the specified `task_id` using the HTTP DELETE method.

        Args:
            task_id (string): task_id

        Returns:
            Any: Returns an empty response when the task was successfully deleted.

        Tags:
            Tasks
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/tasks/{task_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_tasks_id_assignments(self, task_id) -> dict[str, Any]:
        """
        Retrieves the assignments for a specific task identified by the "{task_id}" using the GET method.

        Args:
            task_id (string): task_id

        Returns:
            dict[str, Any]: Returns a collection of task assignment defining what task on
        a file has been assigned to which users and by who.

        Tags:
            Task assignments
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/tasks/{task_id}/assignments"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_task_assignments(self, task=None, assign_to=None) -> dict[str, Any]:
        """
        Creates a new task assignment and returns a task assignment object with a successful creation status.

        Args:
            task (object): The task to assign to a user.
            assign_to (object): The user to assign the task to.

        Returns:
            dict[str, Any]: Returns a new task assignment object.

        Tags:
            Task assignments
        """
        request_body = {
            'task': task,
            'assign_to': assign_to,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task_assignments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_task_assignments_id(self, task_assignment_id) -> dict[str, Any]:
        """
        Retrieves a specific task assignment by its ID using the GET method, returning details about the assignment if found, or an error if it does not exist.

        Args:
            task_assignment_id (string): task_assignment_id

        Returns:
            dict[str, Any]: Returns a task assignment, specifying who the task has been assigned to
        and by whom.

        Tags:
            Task assignments
        """
        if task_assignment_id is None:
            raise ValueError("Missing required parameter 'task_assignment_id'")
        url = f"{self.base_url}/task_assignments/{task_assignment_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_task_assignments_id(self, task_assignment_id, message=None, resolution_state=None) -> dict[str, Any]:
        """
        Updates a task assignment with the specified ID using the PUT method.

        Args:
            task_assignment_id (string): task_assignment_id
            message (string): An optional message by the assignee that can be added to the task. Example: 'Looks good to me'.
            resolution_state (string): The state of the task assigned to the user.

        * For a task with an `action` value of `complete` this can be
        `incomplete` or `completed`.
        * For a task with an `action` of `review` this can be
        `incomplete`, `approved`, or `rejected`. Example: 'completed'.

        Returns:
            dict[str, Any]: Returns the updated task assignment object.

        Tags:
            Task assignments
        """
        if task_assignment_id is None:
            raise ValueError("Missing required parameter 'task_assignment_id'")
        request_body = {
            'message': message,
            'resolution_state': resolution_state,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task_assignments/{task_assignment_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_task_assignments_id(self, task_assignment_id) -> Any:
        """
        Deletes a task assignment by ID using the "DELETE" method, provided that the task assignment has no associated time entries.

        Args:
            task_assignment_id (string): task_assignment_id

        Returns:
            Any: Returns an empty response when the task
        assignment was successfully deleted.

        Tags:
            Task assignments
        """
        if task_assignment_id is None:
            raise ValueError("Missing required parameter 'task_assignment_id'")
        url = f"{self.base_url}/task_assignments/{task_assignment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shared_items(self, fields=None) -> dict[str, Any]:
        """
        Retrieves information about shared items using a shared link via the Box API, allowing for optional specification of fields to include in the response.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a full file resource if the shared link is valid and
        the user has access to it.

        Tags:
            Shared links (Files)
        """
        url = f"{self.base_url}/shared_items"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_files_id_get_shared_link(self, file_id, fields) -> dict[str, Any]:
        """
        Retrieves a shared link for a specific file identified by its ID using the "GET" method.

        Args:
            file_id (string): file_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.

        Returns:
            dict[str, Any]: Returns the base representation of a file with the
        additional shared link information.

        Tags:
            Shared links (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/files/{file_id}#get_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_files_id_add_shared_link(self, file_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Generates a shared link for a specific file identified by `file_id`, optionally retrieving specified fields, using the PUT method at the path "/files/{file_id}#add_shared_link".

        Args:
            file_id (string): file_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): The settings for the shared link to create on the file.
        Use an empty object (`{}`) to use the default settings for shared
        links.

        Returns:
            dict[str, Any]: Returns the base representation of a file with a new shared
        link attached.

        Tags:
            Shared links (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}#add_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_files_id_update_shared_link(self, file_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Updates the shared link settings for a specific file using the PUT method, allowing modifications to access permissions and other link properties for the file identified by the file_id parameter.

        Args:
            file_id (string): file_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): The settings for the shared link to update.

        Returns:
            dict[str, Any]: Returns a basic representation of the file, with the updated shared
        link attached.

        Tags:
            Shared links (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}#update_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_files_id_remove_shared_link(self, file_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Removes a shared link from a file using the Box API by setting the `shared_link` field to `null` via a PUT request to the specified file ID endpoint.

        Args:
            file_id (string): file_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): By setting this value to `null`, the shared link
        is removed from the file.

        Returns:
            dict[str, Any]: Returns a basic representation of a file, with the shared link removed.

        Tags:
            Shared links (Files)
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_id}#remove_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shared_items_folders(self, fields=None) -> dict[str, Any]:
        """
        Retrieves a list of shared folder items using the Box API, with optional filtering by specified fields, and returns them in a formatted response.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a full folder resource if the shared link is valid and
        the user has access to it.

        Tags:
            Shared links (Folders)
        """
        url = f"{self.base_url}/shared_items#folders"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_id_get_shared_link(self, folder_id, fields) -> dict[str, Any]:
        """
        Generates a shared link for a specific folder identified by the `{folder_id}` using the GET method, returning the link in the response.

        Args:
            folder_id (string): folder_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.

        Returns:
            dict[str, Any]: Returns the base representation of a folder with the
        additional shared link information.

        Tags:
            Shared links (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folders/{folder_id}#get_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_folders_id_add_shared_link(self, folder_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Adds a shared link to a folder using the "PUT" method by specifying the folder ID in the URL and optionally customizing the response fields via query parameters.

        Args:
            folder_id (string): folder_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): The settings for the shared link to create on the folder.

        Use an empty object (`{}`) to use the default settings for shared
        links.

        Returns:
            dict[str, Any]: Returns the base representation of a folder with a new shared
        link attached.

        Tags:
            Shared links (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folder_id}#add_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_folders_id_update_shared_link(self, folder_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Updates the shared link settings for a specified folder using the "PUT" method, returning a representation of the folder with the updated shared link.

        Args:
            folder_id (string): folder_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): The settings for the shared link to update.

        Returns:
            dict[str, Any]: Returns a basic representation of the folder, with the updated shared
        link attached.

        Tags:
            Shared links (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folder_id}#update_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_folders_id_remove_shared_link(self, folder_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Removes a shared link from a specified folder using the Box API and returns a basic representation of the folder.

        Args:
            folder_id (string): folder_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): By setting this value to `null`, the shared link
        is removed from the folder.

        Returns:
            dict[str, Any]: Returns a basic representation of a folder, with the shared link removed.

        Tags:
            Shared links (Folders)
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folder_id}#remove_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_web_links(self, url=None, parent=None, name=None, description=None) -> dict[str, Any]:
        """
        Submits a new web link to the server using the POST method at the "/web_links" path and returns a status message.

        Args:
            url (string): The URL that this web link links to. Must start with
        `"http://"` or `"https://"`. Example: 'https://box.com'.
            parent (object): The parent folder to create the web link within.
            name (string): Name of the web link. Defaults to the URL if not set. Example: 'Box Website'.
            description (string): Description of the web link. Example: 'Cloud Content Management'.

        Returns:
            dict[str, Any]: Returns the newly created web link object.

        Tags:
            Web links
        """
        request_body = {
            'url': url,
            'parent': parent,
            'name': name,
            'description': description,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/web_links"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_web_links_id(self, web_link_id) -> dict[str, Any]:
        """
        Retrieves information about a specific web link using its ID, identified by the path "/web_links/{web_link_id}", via a GET request.

        Args:
            web_link_id (string): web_link_id

        Returns:
            dict[str, Any]: Returns the web link object.

        Tags:
            Web links
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        url = f"{self.base_url}/web_links/{web_link_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_web_links_id(self, web_link_id, fields=None, name=None, parent=None) -> dict[str, Any]:
        """
        Creates a new resource associated with a specific web link identified by `{web_link_id}` and returns a status message, optionally including specified fields.

        Args:
            web_link_id (string): web_link_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): An optional new name for the web link. Example: 'Restored.docx'.
            parent (string): parent

        Returns:
            dict[str, Any]: Returns a web link object when it has been restored.

        Tags:
            Trashed web links
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        request_body = {
            'name': name,
            'parent': parent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/web_links/{web_link_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_web_links_id(self, web_link_id, url=None, parent=None, name=None, description=None, shared_link=None) -> dict[str, Any]:
        """
        Updates a web link resource identified by the `web_link_id` using the HTTP PUT method.

        Args:
            web_link_id (string): web_link_id
            url (string): The new URL that the web link links to. Must start with
        `"http://"` or `"https://"`. Example: 'https://box.com'.
            parent (string): parent
            name (string): A new name for the web link. Defaults to the URL if not set. Example: 'Box Website'.
            description (string): A new description of the web link. Example: 'Cloud Content Management'.
            shared_link (object): The settings for the shared link to update.

        Returns:
            dict[str, Any]: Returns the updated web link object.

        Tags:
            Web links
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        request_body = {
            'url': url,
            'parent': parent,
            'name': name,
            'description': description,
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/web_links/{web_link_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_web_links_id(self, web_link_id) -> Any:
        """
        Deletes a web link resource identified by its ID from the system using the DELETE method.

        Args:
            web_link_id (string): web_link_id

        Returns:
            Any: An empty response will be returned when the web link
        was successfully deleted.

        Tags:
            Web links
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        url = f"{self.base_url}/web_links/{web_link_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_web_links_id_trash(self, web_link_id, fields=None) -> dict[str, Any]:
        """
        Retrieves information about a trashed web link by its ID, allowing for optional specification of fields to include in the response.

        Args:
            web_link_id (string): web_link_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the web link that was trashed,
        including information about when the it
        was moved to the trash.

        Tags:
            Trashed web links
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        url = f"{self.base_url}/web_links/{web_link_id}/trash"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_web_links_id_trash(self, web_link_id) -> Any:
        """
        Deletes a web link by moving it to the trash using the provided web link ID.

        Args:
            web_link_id (string): web_link_id

        Returns:
            Any: Returns an empty response when the web link was
        permanently deleted.

        Tags:
            Trashed web links
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        url = f"{self.base_url}/web_links/{web_link_id}/trash"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shared_items_web_links(self, fields=None) -> dict[str, Any]:
        """
        Retrieves a list of web links for shared items using the GET method at the "/shared_items#web_links" endpoint.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a full web link resource if the shared link is valid and
        the user has access to it.

        Tags:
            Shared links (Web Links)
        """
        url = f"{self.base_url}/shared_items#web_links"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_web_links_id_get_shared_link(self, web_link_id, fields) -> dict[str, Any]:
        """
        Retrieves details of a shared web link using its unique identifier and optional field selection parameters.

        Args:
            web_link_id (string): web_link_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.

        Returns:
            dict[str, Any]: Returns the base representation of a web link with the
        additional shared link information.

        Tags:
            Shared links (Web Links)
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        url = f"{self.base_url}/web_links/{web_link_id}#get_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_web_links_id_add_shared_link(self, web_link_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Adds a shared link to a specified web link, allowing it to be accessed and shared by others, using the Box API.

        Args:
            web_link_id (string): web_link_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): The settings for the shared link to create on the web link.

        Use an empty object (`{}`) to use the default settings for shared
        links.

        Returns:
            dict[str, Any]: Returns the base representation of a web link with a new shared
        link attached.

        Tags:
            Shared links (Web Links)
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/web_links/{web_link_id}#add_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_web_links_id_update_shared_link(self, web_link_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Updates a shared link for a web link identified by the `{web_link_id}` and optionally specifies fields to include in the response using the `fields` query parameter.

        Args:
            web_link_id (string): web_link_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): The settings for the shared link to update.

        Returns:
            dict[str, Any]: Returns a basic representation of the web link, with the updated shared
        link attached.

        Tags:
            Shared links (Web Links)
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/web_links/{web_link_id}#update_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_web_links_id_remove_shared_link(self, web_link_id, fields, shared_link=None) -> dict[str, Any]:
        """
        Removes a shared link from a web link resource using the `PUT` method by setting the shared link to null for the specified `web_link_id`.

        Args:
            web_link_id (string): web_link_id
            fields (string): Explicitly request the `shared_link` fields
        to be returned for this item. Example: 'shared_link'.
            shared_link (object): By setting this value to `null`, the shared link
        is removed from the web link.

        Returns:
            dict[str, Any]: Returns a basic representation of a web link, with the
        shared link removed.

        Tags:
            Shared links (Web Links)
        """
        if web_link_id is None:
            raise ValueError("Missing required parameter 'web_link_id'")
        request_body = {
            'shared_link': shared_link,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/web_links/{web_link_id}#remove_shared_link"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shared_items_app_items(self) -> dict[str, Any]:
        """
        Retrieves information about a shared file or folder using a shared link provided in the `boxapi` header.

        Returns:
            dict[str, Any]: Returns a full app item resource if the shared link is valid and
        the user has access to it.

        Tags:
            Shared links (App Items)
        """
        url = f"{self.base_url}/shared_items#app_items"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users(self, filter_term=None, user_type=None, external_app_user_id=None, fields=None, offset=None, limit=None, usemarker=None, marker=None) -> dict[str, Any]:
        """
        Retrieves a filtered or paginated list of users, supporting optional query parameters for filtering, field selection, and result pagination.

        Args:
            filter_term (string): Limits the results to only users who's `name` or
        `login` start with the search term. For externally managed users, the search term needs
        to completely match the in order to find the user, and
        it will only return one user at a time. Example: 'john'.
            user_type (string): Limits the results to the kind of user specified. * `all` returns every kind of user for whom the `login` or `name` partially matches the `filter_term`. It will only return an external user if the login matches the `filter_term` completely, and in that case it will only return that user.
        * `managed` returns all managed and app users for whom the `login` or `name` partially matches the `filter_term`.
        * `external` returns all external users for whom the `login` matches the `filter_term` exactly. Example: 'managed'.
            external_app_user_id (string): Limits the results to app users with the given
        `external_app_user_id` value. When creating an app user, an
        `external_app_user_id` value can be set. This value can
        then be used in this endpoint to find any users that
        match that `external_app_user_id` value. Example: 'my-user-1234'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            usemarker (boolean): Specifies whether to use marker-based pagination instead of
        offset-based pagination. Only one pagination method can
        be used at a time. By setting this value to true, the API will return a `marker` field
        that can be passed as a parameter to this endpoint to get the next
        page of the response. Example: 'True'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.

        Returns:
            dict[str, Any]: Returns all of the users in the enterprise.

        Tags:
            Users
        """
        url = f"{self.base_url}/users"
        query_params = {k: v for k, v in [('filter_term', filter_term), ('user_type', user_type), ('external_app_user_id', external_app_user_id), ('fields', fields), ('offset', offset), ('limit', limit), ('usemarker', usemarker), ('marker', marker)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_users(self, fields=None, name=None, login=None, is_platform_access_only=None, role=None, language=None, is_sync_enabled=None, job_title=None, phone=None, address=None, space_amount=None, tracking_codes=None, can_see_managed_users=None, timezone=None, is_external_collab_restricted=None, is_exempt_from_device_limits=None, is_exempt_from_login_verification=None, status=None, external_app_user_id=None) -> dict[str, Any]:
        """
        Creates a new user in the system using the "POST" method at the "/users" endpoint, allowing for dynamic management of user accounts.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): The name of the user Example: 'Aaron Levie'.
            login (string): The email address the user uses to log in

        Required, unless `is_platform_access_only`
        is set to `true`. Example: 'boss@box.com'.
            is_platform_access_only (boolean): Specifies that the user is an app user. Example: 'True'.
            role (string): The user’s enterprise role Example: 'user'.
            language (string): The language of the user, formatted in modified version of the
        [ISO 639-1](/guides/api-calls/language-codes) format. Example: 'en'.
            is_sync_enabled (boolean): Whether the user can use Box Sync Example: 'True'.
            job_title (string): The user’s job title Example: 'CEO'.
            phone (string): The user’s phone number Example: '6509241374'.
            address (string): The user’s address Example: '900 Jefferson Ave, Redwood City, CA 94063'.
            space_amount (integer): The user’s total available space in bytes. Set this to `-1` to
        indicate unlimited storage. Example: '11345156112'.
            tracking_codes (array): Tracking codes allow an admin to generate reports from the
        admin console and assign an attribute to a specific group
        of users. This setting must be enabled for an enterprise before it
        can be used.
            can_see_managed_users (boolean): Whether the user can see other enterprise users in their
        contact list Example: 'True'.
            timezone (string): The user's timezone Example: 'Africa/Bujumbura'.
            is_external_collab_restricted (boolean): Whether the user is allowed to collaborate with users outside
        their enterprise Example: 'True'.
            is_exempt_from_device_limits (boolean): Whether to exempt the user from enterprise device limits Example: 'True'.
            is_exempt_from_login_verification (boolean): Whether the user must use two-factor authentication Example: 'True'.
            status (string): The user's account status Example: 'active'.
            external_app_user_id (string): An external identifier for an app user, which can be used to look
        up the user. This can be used to tie user IDs from external
        identity providers to Box users. Example: 'my-user-1234'.

        Returns:
            dict[str, Any]: Returns a user object for the newly created user.

        Tags:
            Users
        """
        request_body = {
            'name': name,
            'login': login,
            'is_platform_access_only': is_platform_access_only,
            'role': role,
            'language': language,
            'is_sync_enabled': is_sync_enabled,
            'job_title': job_title,
            'phone': phone,
            'address': address,
            'space_amount': space_amount,
            'tracking_codes': tracking_codes,
            'can_see_managed_users': can_see_managed_users,
            'timezone': timezone,
            'is_external_collab_restricted': is_external_collab_restricted,
            'is_exempt_from_device_limits': is_exempt_from_device_limits,
            'is_exempt_from_login_verification': is_exempt_from_login_verification,
            'status': status,
            'external_app_user_id': external_app_user_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/users"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_me(self, fields=None) -> dict[str, Any]:
        """
        Retrieves the current authenticated user's profile and allows filtering the response fields with an optional query parameter.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a single user object.

        Tags:
            Users
        """
        url = f"{self.base_url}/users/me"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_users_terminate_sessions(self, user_ids=None, user_logins=None) -> dict[str, Any]:
        """
        Terminates a user's active sessions by creating asynchronous jobs and returns the request status.

        Args:
            user_ids (array): A list of user IDs Example: "['123456', '456789']".
            user_logins (array): A list of user logins Example: "['user@sample.com', 'user2@sample.com']".

        Returns:
            dict[str, Any]: Returns a message about the request status.

        Tags:
            Session termination
        """
        request_body = {
            'user_ids': user_ids,
            'user_logins': user_logins,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/users/terminate_sessions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_id(self, user_id, fields=None) -> dict[str, Any]:
        """
        Retrieves details for a specific user identified by user_id, optionally filtering the returned fields.

        Args:
            user_id (string): user_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a single user object.

        Not all available fields are returned by default. Use the
        [fields](#param-fields) query parameter to explicitly request
        any specific fields using the [fields](#get-users-id--request--fields)
        parameter.

        Tags:
            Users
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/users/{user_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_users_id(self, user_id, fields=None, enterprise=None, notify=None, name=None, login=None, role=None, language=None, is_sync_enabled=None, job_title=None, phone=None, address=None, tracking_codes=None, can_see_managed_users=None, timezone=None, is_external_collab_restricted=None, is_exempt_from_device_limits=None, is_exempt_from_login_verification=None, is_password_reset_required=None, status=None, space_amount=None, notification_email=None, external_app_user_id=None) -> dict[str, Any]:
        """
        Updates or replaces the details of a user identified by the provided user_id.

        Args:
            user_id (string): user_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            enterprise (string): Set this to `null` to roll the user out of the enterprise
        and make them a free user
            notify (boolean): Whether the user should receive an email when they
        are rolled out of an enterprise Example: 'True'.
            name (string): The name of the user Example: 'Aaron Levie'.
            login (string): The email address the user uses to log in

        Note: If the target user's email is not confirmed, then the
        primary login address cannot be changed. Example: 'somename@box.com'.
            role (string): The user’s enterprise role Example: 'user'.
            language (string): The language of the user, formatted in modified version of the
        [ISO 639-1](/guides/api-calls/language-codes) format. Example: 'en'.
            is_sync_enabled (boolean): Whether the user can use Box Sync Example: 'True'.
            job_title (string): The user’s job title Example: 'CEO'.
            phone (string): The user’s phone number Example: '6509241374'.
            address (string): The user’s address Example: '900 Jefferson Ave, Redwood City, CA 94063'.
            tracking_codes (array): Tracking codes allow an admin to generate reports from the
        admin console and assign an attribute to a specific group
        of users. This setting must be enabled for an enterprise before it
        can be used.
            can_see_managed_users (boolean): Whether the user can see other enterprise users in their
        contact list Example: 'True'.
            timezone (string): The user's timezone Example: 'Africa/Bujumbura'.
            is_external_collab_restricted (boolean): Whether the user is allowed to collaborate with users outside
        their enterprise Example: 'True'.
            is_exempt_from_device_limits (boolean): Whether to exempt the user from enterprise device limits Example: 'True'.
            is_exempt_from_login_verification (boolean): Whether the user must use two-factor authentication Example: 'True'.
            is_password_reset_required (boolean): Whether the user is required to reset their password Example: 'True'.
            status (string): The user's account status Example: 'active'.
            space_amount (integer): The user’s total available space in bytes. Set this to `-1` to
        indicate unlimited storage. Example: '11345156112'.
            notification_email (object): An alternate notification email address to which email
        notifications are sent. When it's confirmed, this will be
        the email address to which notifications are sent instead of
        to the primary email address.

        Set this value to `null` to remove the notification email.
            external_app_user_id (string): An external identifier for an app user, which can be used to look
        up the user. This can be used to tie user IDs from external
        identity providers to Box users.

        Note: In order to update this field, you need to request a token
        using the application that created the app user. Example: 'my-user-1234'.

        Returns:
            dict[str, Any]: Returns the updated user object.

        Tags:
            Users
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        request_body = {
            'enterprise': enterprise,
            'notify': notify,
            'name': name,
            'login': login,
            'role': role,
            'language': language,
            'is_sync_enabled': is_sync_enabled,
            'job_title': job_title,
            'phone': phone,
            'address': address,
            'tracking_codes': tracking_codes,
            'can_see_managed_users': can_see_managed_users,
            'timezone': timezone,
            'is_external_collab_restricted': is_external_collab_restricted,
            'is_exempt_from_device_limits': is_exempt_from_device_limits,
            'is_exempt_from_login_verification': is_exempt_from_login_verification,
            'is_password_reset_required': is_password_reset_required,
            'status': status,
            'space_amount': space_amount,
            'notification_email': notification_email,
            'external_app_user_id': external_app_user_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/users/{user_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_users_id(self, user_id, notify=None, force=None) -> Any:
        """
        Deletes a user by user ID, optionally notifying or forcing the deletion, and returns a successful status if the operation is completed.

        Args:
            user_id (string): user_id
            notify (boolean): Whether the user will receive email notification of
        the deletion Example: 'True'.
            force (boolean): Whether the user should be deleted even if this user
        still own files Example: 'True'.

        Returns:
            Any: Removes the user and returns an empty response.

        Tags:
            Users
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/users/{user_id}"
        query_params = {k: v for k, v in [('notify', notify), ('force', force)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_id_avatar(self, user_id) -> Any:
        """
        Retrieves the avatar image for the specified user.

        Args:
            user_id (string): user_id

        Returns:
            Any: When an avatar can be found for the user the
        image data will be returned in the body of the
        response.

        Tags:
            User avatars
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/users/{user_id}/avatar"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()


    def delete_users_id_avatar(self, user_id) -> Any:
        """
        Removes the avatar image associated with the specified user.

        Args:
            user_id (string): user_id

        Returns:
            Any: * `no_content`: Removes the avatar and returns an empty response.

        Tags:
            User avatars
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/users/{user_id}/avatar"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_users_id_folders_0(self, user_id, fields=None, notify=None, owned_by=None) -> dict[str, Any]:
        """
        Updates the details of the root folder (folder ID 0) for a specified user, optionally specifying fields to return and notification preferences.

        Args:
            user_id (string): user_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            notify (boolean): Determines if users should receive email notification
        for the action performed. Example: 'True'.
            owned_by (object): The user who the folder will be transferred to

        Returns:
            dict[str, Any]: Returns the information for the newly created
        destination folder.

        Tags:
            Transfer folders
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        request_body = {
            'owned_by': owned_by,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/users/{user_id}/folders/0"
        query_params = {k: v for k, v in [('fields', fields), ('notify', notify)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_id_email_aliases(self, user_id) -> dict[str, Any]:
        """
        Retrieves a list of email aliases for a specific user using the "GET" method, identified by their unique user ID.

        Args:
            user_id (string): user_id

        Returns:
            dict[str, Any]: Returns a collection of email aliases.

        Tags:
            Email aliases
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/users/{user_id}/email_aliases"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_users_id_email_aliases(self, user_id, email=None) -> dict[str, Any]:
        """
        Creates new email aliases for a specified user using the API endpoint at "/users/{user_id}/email_aliases".

        Args:
            user_id (string): user_id
            email (string): The email address to add to the account as an alias.

        Note: The domain of the email alias needs to be registered
         to your enterprise.
        See the [domain verification guide](
          https://support.box.com/hc/en-us/articles/4408619650579-Domain-Verification
          ) for steps to add a new domain. Example: 'alias@example.com'.

        Returns:
            dict[str, Any]: Returns the newly created email alias object.

        Tags:
            Email aliases
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        request_body = {
            'email': email,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/users/{user_id}/email_aliases"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_users_id_email_aliases_id(self, user_id, email_alias_id) -> Any:
        """
        Deletes an email alias associated with a specific user, identified by the user ID and email alias ID, using the DELETE method.

        Args:
            user_id (string): user_id
            email_alias_id (string): email_alias_id

        Returns:
            Any: Removes the alias and returns an empty response.

        Tags:
            Email aliases
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        if email_alias_id is None:
            raise ValueError("Missing required parameter 'email_alias_id'")
        url = f"{self.base_url}/users/{user_id}/email_aliases/{email_alias_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_id_memberships(self, user_id, limit=None, offset=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of memberships associated with a specified user by user ID.

        Args:
            user_id (string): user_id
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of membership objects. If there are no
        memberships, an empty collection will be returned.

        Tags:
            Group memberships
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/users/{user_id}/memberships"
        query_params = {k: v for k, v in [('limit', limit), ('offset', offset)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_invites(self, fields=None, enterprise=None, actionable_by=None) -> dict[str, Any]:
        """
        Creates a new invite by sending a POST request to the /invites endpoint, optionally specifying fields to include in the response.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            enterprise (object): The enterprise to invite the user to
            actionable_by (object): The user to invite

        Returns:
            dict[str, Any]: Returns a new invite object.

        Tags:
            Invites
        """
        request_body = {
            'enterprise': enterprise,
            'actionable_by': actionable_by,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/invites"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_invites_id(self, invite_id, fields=None) -> dict[str, Any]:
        """
        Retrieves details about a specific invitation, identified by the `invite_id`, optionally including custom fields specified in the query parameters.

        Args:
            invite_id (string): invite_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns an invite object

        Tags:
            Invites
        """
        if invite_id is None:
            raise ValueError("Missing required parameter 'invite_id'")
        url = f"{self.base_url}/invites/{invite_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_groups(self, filter_term=None, fields=None, limit=None, offset=None) -> dict[str, Any]:
        """
        Retrieves a list of groups, optionally filtered and paginated, based on query parameters for filtering, field selection, and result limits.

        Args:
            filter_term (string): Limits the results to only groups whose `name` starts
        with the search term. Example: 'Engineering'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of group objects. If there are no groups, an
        empty collection will be returned.

        Tags:
            Groups
        """
        url = f"{self.base_url}/groups"
        query_params = {k: v for k, v in [('filter_term', filter_term), ('fields', fields), ('limit', limit), ('offset', offset)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_groups(self, fields=None, name=None, provenance=None, external_sync_identifier=None, description=None, invitability_level=None, member_viewability_level=None) -> dict[str, Any]:
        """
        Creates a new group using the API and returns a status message, with optional filtering by specified fields.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): The name of the new group to be created. This name must be unique
        within the enterprise. Example: 'Customer Support'.
            provenance (string): Keeps track of which external source this group is
        coming, for example `Active Directory`, or `Okta`.

        Setting this will also prevent Box admins from editing
        the group name and its members directly via the Box
        web application.

        This is desirable for one-way syncing of groups. Example: 'Active Directory'.
            external_sync_identifier (string): An arbitrary identifier that can be used by
        external group sync tools to link this Box Group to
        an external group.

        Example values of this field
        could be an **Active Directory Object ID** or a **Google
        Group ID**.

        We recommend you use of this field in
        order to avoid issues when group names are updated in
        either Box or external systems. Example: 'AD:123456'.
            description (string): A human readable description of the group. Example: '"Customer Support Group - as imported from Active Directory"'.
            invitability_level (string): Specifies who can invite the group to collaborate
        on folders.

        When set to `admins_only` the enterprise admin, co-admins,
        and the group's admin can invite the group.

        When set to `admins_and_members` all the admins listed
        above and group members can invite the group.

        When set to `all_managed_users` all managed users in the
        enterprise can invite the group. Example: 'admins_only'.
            member_viewability_level (string): Specifies who can see the members of the group.

        * `admins_only` - the enterprise admin, co-admins, group's
          group admin
        * `admins_and_members` - all admins and group members
        * `all_managed_users` - all managed users in the
          enterprise Example: 'admins_only'.

        Returns:
            dict[str, Any]: Returns the new group object.

        Tags:
            Groups
        """
        request_body = {
            'name': name,
            'provenance': provenance,
            'external_sync_identifier': external_sync_identifier,
            'description': description,
            'invitability_level': invitability_level,
            'member_viewability_level': member_viewability_level,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/groups"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_groups_terminate_sessions(self, group_ids=None) -> dict[str, Any]:
        """
        Terminates active sessions for a specified group using a POST request to the "/groups/terminate_sessions" API endpoint.

        Args:
            group_ids (array): A list of group IDs Example: "['123456', '456789']".

        Returns:
            dict[str, Any]: Returns a message about the request status.

        Tags:
            Session termination
        """
        request_body = {
            'group_ids': group_ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/groups/terminate_sessions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_groups_id(self, group_id, fields=None) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific group identified by the group_id, optionally filtering the returned data based on specified fields.

        Args:
            group_id (string): group_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the group object

        Tags:
            Groups
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group_id'")
        url = f"{self.base_url}/groups/{group_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_groups_id(self, group_id, fields=None, name=None, provenance=None, external_sync_identifier=None, description=None, invitability_level=None, member_viewability_level=None) -> dict[str, Any]:
        """
        Updates the details of a specific group identified by the group_id path parameter, with optional field selection via the fields query parameter, and returns a status response.

        Args:
            group_id (string): group_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            name (string): The name of the new group to be created. Must be unique within the
        enterprise. Example: 'Customer Support'.
            provenance (string): Keeps track of which external source this group is
        coming, for example `Active Directory`, or `Okta`.

        Setting this will also prevent Box admins from editing
        the group name and its members directly via the Box
        web application.

        This is desirable for one-way syncing of groups. Example: 'Active Directory'.
            external_sync_identifier (string): An arbitrary identifier that can be used by
        external group sync tools to link this Box Group to
        an external group.

        Example values of this field
        could be an **Active Directory Object ID** or a **Google
        Group ID**.

        We recommend you use of this field in
        order to avoid issues when group names are updated in
        either Box or external systems. Example: 'AD:123456'.
            description (string): A human readable description of the group. Example: '"Customer Support Group - as imported from Active Directory"'.
            invitability_level (string): Specifies who can invite the group to collaborate
        on folders.

        When set to `admins_only` the enterprise admin, co-admins,
        and the group's admin can invite the group.

        When set to `admins_and_members` all the admins listed
        above and group members can invite the group.

        When set to `all_managed_users` all managed users in the
        enterprise can invite the group. Example: 'admins_only'.
            member_viewability_level (string): Specifies who can see the members of the group.

        * `admins_only` - the enterprise admin, co-admins, group's
          group admin
        * `admins_and_members` - all admins and group members
        * `all_managed_users` - all managed users in the
          enterprise Example: 'admins_only'.

        Returns:
            dict[str, Any]: Returns the updated group object.

        Tags:
            Groups
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group_id'")
        request_body = {
            'name': name,
            'provenance': provenance,
            'external_sync_identifier': external_sync_identifier,
            'description': description,
            'invitability_level': invitability_level,
            'member_viewability_level': member_viewability_level,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/groups/{group_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_groups_id(self, group_id) -> Any:
        """
        Deletes the group identified by the specified group ID.

        Args:
            group_id (string): group_id

        Returns:
            Any: A blank response is returned if the group was
        successfully deleted.

        Tags:
            Groups
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group_id'")
        url = f"{self.base_url}/groups/{group_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_groups_id_memberships(self, group_id, limit=None, offset=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of memberships for a specified group by its group_id.

        Args:
            group_id (string): group_id
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of membership objects. If there are no
        memberships, an empty collection will be returned.

        Tags:
            Group memberships
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group_id'")
        url = f"{self.base_url}/groups/{group_id}/memberships"
        query_params = {k: v for k, v in [('limit', limit), ('offset', offset)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_groups_id_collaborations(self, group_id, limit=None, offset=None) -> dict[str, Any]:
        """
        Retrieves a list of collaborations for a specified group, supporting pagination with optional limit and offset query parameters.

        Args:
            group_id (string): group_id
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of collaboration objects. If there are no
        collaborations, an empty collection will be returned.

        Tags:
            Collaborations (List)
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group_id'")
        url = f"{self.base_url}/groups/{group_id}/collaborations"
        query_params = {k: v for k, v in [('limit', limit), ('offset', offset)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_group_memberships(self, fields=None, user=None, group=None, role=None, configurable_permissions=None) -> dict[str, Any]:
        """
        Creates a new group membership by adding an agent or user to a specified group.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            user (object): The user to add to the group.
            group (object): The group to add the user to.
            role (string): The role of the user in the group. Example: 'member'.
            configurable_permissions (object): Custom configuration for the permissions an admin
        if a group will receive. This option has no effect
        on members with a role of `member`.

        Setting these permissions overwrites the default
        access levels of an admin.

        Specifying a value of `null` for this object will disable
        all configurable permissions. Specifying permissions will set
        them accordingly, omitted permissions will be enabled by default. Example: "{'can_run_reports': True}".

        Returns:
            dict[str, Any]: Returns a new group membership object.

        Tags:
            Group memberships
        """
        request_body = {
            'user': user,
            'group': group,
            'role': role,
            'configurable_permissions': configurable_permissions,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/group_memberships"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_group_memberships_id(self, group_membership_id, fields=None) -> dict[str, Any]:
        """
        Retrieves information about a specific group membership using the Zendesk API, returning details about the specified membership based on the provided `group_membership_id`.

        Args:
            group_membership_id (string): group_membership_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the group membership object.

        Tags:
            Group memberships
        """
        if group_membership_id is None:
            raise ValueError("Missing required parameter 'group_membership_id'")
        url = f"{self.base_url}/group_memberships/{group_membership_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_group_memberships_id(self, group_membership_id, fields=None, role=None, configurable_permissions=None) -> dict[str, Any]:
        """
        Updates the details of a specific group membership identified by group_membership_id.

        Args:
            group_membership_id (string): group_membership_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            role (string): The role of the user in the group. Example: 'member'.
            configurable_permissions (object): Custom configuration for the permissions an admin
        if a group will receive. This option has no effect
        on members with a role of `member`.

        Setting these permissions overwrites the default
        access levels of an admin.

        Specifying a value of `null` for this object will disable
        all configurable permissions. Specifying permissions will set
        them accordingly, omitted permissions will be enabled by default. Example: "{'can_run_reports': True}".

        Returns:
            dict[str, Any]: Returns a new group membership object.

        Tags:
            Group memberships
        """
        if group_membership_id is None:
            raise ValueError("Missing required parameter 'group_membership_id'")
        request_body = {
            'role': role,
            'configurable_permissions': configurable_permissions,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/group_memberships/{group_membership_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_group_memberships_id(self, group_membership_id) -> Any:
        """
        Deletes a specific group membership identified by group_membership_id, removing the user from the group without returning content.

        Args:
            group_membership_id (string): group_membership_id

        Returns:
            Any: A blank response is returned if the membership was
        successfully deleted.

        Tags:
            Group memberships
        """
        if group_membership_id is None:
            raise ValueError("Missing required parameter 'group_membership_id'")
        url = f"{self.base_url}/group_memberships/{group_membership_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_webhooks(self, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of registered webhooks with optional marker and limit query parameters.

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a list of webhooks.

        Tags:
            Webhooks
        """
        url = f"{self.base_url}/webhooks"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_webhooks(self, target=None, address=None, triggers=None) -> dict[str, Any]:
        """
        Handles incoming webhook POST requests to receive, verify, and process event notifications from external systems.

        Args:
            target (object): The item that will trigger the webhook
            address (string): The URL that is notified by this webhook Example: 'https://example.com/webhooks'.
            triggers (array): An array of event names that this webhook is
        to be triggered for Example: "['FILE.UPLOADED']".

        Returns:
            dict[str, Any]: Returns the new webhook object.

        Tags:
            Webhooks
        """
        request_body = {
            'target': target,
            'address': address,
            'triggers': triggers,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/webhooks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_webhooks_id(self, webhook_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific webhook identified by its webhook_id.

        Args:
            webhook_id (string): webhook_id

        Returns:
            dict[str, Any]: Returns a webhook object

        Tags:
            Webhooks
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/webhooks/{webhook_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_webhooks_id(self, webhook_id, target=None, address=None, triggers=None) -> dict[str, Any]:
        """
        Updates an existing webhook with the specified ID using the PUT method, allowing modifications to the webhook's details.

        Args:
            webhook_id (string): webhook_id
            target (object): The item that will trigger the webhook
            address (string): The URL that is notified by this webhook Example: 'https://example.com/webhooks'.
            triggers (array): An array of event names that this webhook is
        to be triggered for Example: "['FILE.UPLOADED']".

        Returns:
            dict[str, Any]: Returns the new webhook object.

        Tags:
            Webhooks
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        request_body = {
            'target': target,
            'address': address,
            'triggers': triggers,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/webhooks/{webhook_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_webhooks_id(self, webhook_id) -> Any:
        """
        Deletes a webhook specified by its ID using the DELETE method, allowing for the removal of unnecessary webhooks and optimizing system resources.

        Args:
            webhook_id (string): webhook_id

        Returns:
            Any: An empty response will be returned when the webhook
        was successfully deleted.

        Tags:
            Webhooks
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/webhooks/{webhook_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_skill_invocations_id(self, skill_id, status=None, metadata=None, file=None, file_version=None, usage=None) -> Any:
        """
        Invokes or updates a skill with the specified ID using the PUT method, returning a response based on the operation's success or failure status.

        Args:
            skill_id (string): skill_id
            status (string): Defines the status of this invocation. Set this to `success` when setting Skill cards. Example: 'success'.
            metadata (object): The metadata to set for this skill. This is a list of
        Box Skills cards. These cards will overwrite any existing Box
        skill cards on the file.
            file (object): The file to assign the cards to.
            file_version (object): The optional file version to assign the cards to.
            usage (object): A descriptor that defines what items are affected by this call.

        Set this to the default values when setting a card to a `success`
        state, and leave it out in most other situations.

        Returns:
            Any: Returns an empty response when the card has been successfully updated.

        Tags:
            Skills
        """
        if skill_id is None:
            raise ValueError("Missing required parameter 'skill_id'")
        request_body = {
            'status': status,
            'metadata': metadata,
            'file': file,
            'file_version': file_version,
            'usage': usage,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/skill_invocations/{skill_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def options_events(self) -> dict[str, Any]:
        """
        Retrieves the communication options and supported HTTP methods available for the "/events" resource.

        Returns:
            dict[str, Any]: Returns a paginated array of servers that can be used
        instead of the regular endpoints for long-polling events.

        Tags:
            Events
        """
        url = f"{self.base_url}/events"
        query_params = {}
        response = self._options(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_events(self, stream_type=None, stream_position=None, limit=None, event_type=None, created_after=None, created_before=None) -> dict[str, Any]:
        """
        Retrieves a list of events based on specified filters such as stream type, stream position, event type, and creation time, using the "GET" method at the "/events" endpoint.

        Args:
            stream_type (string): Defines the type of events that are returned * `all` returns everything for a user and is the default
        * `changes` returns events that may cause file tree changes such as file updates or collaborations.
        * `sync` is similar to `changes` but only applies to synced folders
        * `admin_logs` returns all events for an entire enterprise and requires the user making the API call to have admin permissions. This stream type is for programmatically pulling from a 1 year history of events across all users within the enterprise and within a `created_after` and `created_before` time frame. The complete history of events will be returned in chronological order based on the event time, but latency will be much higher than `admin_logs_streaming`.
        * `admin_logs_streaming` returns all events for an entire enterprise and requires the user making the API call to have admin permissions. This stream type is for polling for recent events across all users within the enterprise. Latency will be much lower than `admin_logs`, but events will not be returned in chronological order and may contain duplicates. Example: 'all'.
            stream_position (string): The location in the event stream to start receiving events from. * `now` will return an empty list events and
        the latest stream position for initialization.
        * `0` or `null` will return all events. Example: '1348790499819'.
            limit (integer): Limits the number of events returned Note: Sometimes, the events less than the limit requested can be returned
        even when there may be more events remaining. This is primarily done in
        the case where a number of events have already been retrieved and these
        retrieved events are returned rather than delaying for an unknown amount
        of time to see if there are any more results. Example: '50'.
            event_type (array): A comma-separated list of events to filter by. This can only be used when
        requesting the events with a `stream_type` of `admin_logs` or
        `adming_logs_streaming`. For any other `stream_type` this value will be
        ignored. Example: "['ACCESS_GRANTED']".
            created_after (string): The lower bound date and time to return events for. This can only be used
        when requesting the events with a `stream_type` of `admin_logs`. For any
        other `stream_type` this value will be ignored. Example: '2012-12-12T10:53:43-08:00'.
            created_before (string): The upper bound date and time to return events for. This can only be used
        when requesting the events with a `stream_type` of `admin_logs`. For any
        other `stream_type` this value will be ignored. Example: '2013-12-12T10:53:43-08:00'.

        Returns:
            dict[str, Any]: Returns a list of event objects.

        Events objects are returned in pages, with each page (chunk)
        including a list of event objects. The response includes a
        `chunk_size` parameter indicating how many events were returned in this
        chunk, as well as the next `stream_position` that can be
        queried.

        Tags:
            Events
        """
        url = f"{self.base_url}/events"
        query_params = {k: v for k, v in [('stream_type', stream_type), ('stream_position', stream_position), ('limit', limit), ('event_type', event_type), ('created_after', created_after), ('created_before', created_before)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collections(self, fields=None, offset=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of collections with optional filtering by specified fields, starting from a given offset, and limited to a specified number of results using the "GET" method at the path "/collections".

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns all collections for the given user

        Tags:
            Collections
        """
        url = f"{self.base_url}/collections"
        query_params = {k: v for k, v in [('fields', fields), ('offset', offset), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collections_id_items(self, collection_id, fields=None, offset=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of items from a specified collection, optionally filtered by selected fields.

        Args:
            collection_id (string): collection_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            offset (integer): The offset of the item at which to begin the response. Queries with offset parameter value
        exceeding 10000 will be rejected
        with a 400 response. Example: '1000'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns an array of items in the collection.

        Tags:
            Collections
        """
        if collection_id is None:
            raise ValueError("Missing required parameter 'collection_id'")
        url = f"{self.base_url}/collections/{collection_id}/items"
        query_params = {k: v for k, v in [('fields', fields), ('offset', offset), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collections_id(self, collection_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific collection identified by the collection_id.

        Args:
            collection_id (string): collection_id

        Returns:
            dict[str, Any]: Returns an array of items in the collection.

        Tags:
            Collections
        """
        if collection_id is None:
            raise ValueError("Missing required parameter 'collection_id'")
        url = f"{self.base_url}/collections/{collection_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_recent_items(self, fields=None, limit=None, marker=None) -> dict[str, Any]:
        """
        Retrieves a list of recent items using the "GET" method at the "/recent_items" path, allowing customization with fields, limit, and marker parameters.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.

        Returns:
            dict[str, Any]: Returns a list recent items access by a user.

        Tags:
            Recent items
        """
        url = f"{self.base_url}/recent_items"
        query_params = {k: v for k, v in [('fields', fields), ('limit', limit), ('marker', marker)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_retention_policies(self, policy_name=None, policy_type=None, created_by_user_id=None, fields=None, limit=None, marker=None) -> dict[str, Any]:
        """
        Retrieves a list of retention policies with optional filtering by name, type, creator, fields, limit, and pagination marker.

        Args:
            policy_name (string): Filters results by a case sensitive prefix of the name of
        retention policies. Example: 'Sales Policy'.
            policy_type (string): Filters results by the type of retention policy. Example: 'finite'.
            created_by_user_id (string): Filters results by the ID of the user who created policy. Example: '21312321'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.

        Returns:
            dict[str, Any]: Returns a list retention policies in the enterprise.

        Tags:
            Retention policies
        """
        url = f"{self.base_url}/retention_policies"
        query_params = {k: v for k, v in [('policy_name', policy_name), ('policy_type', policy_type), ('created_by_user_id', created_by_user_id), ('fields', fields), ('limit', limit), ('marker', marker)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_retention_policies(self, policy_name=None, description=None, policy_type=None, disposition_action=None, retention_length=None, retention_type=None, can_owner_extend_retention=None, are_owners_notified=None, custom_notification_recipients=None) -> dict[str, Any]:
        """
        Creates a new data retention policy using the API and returns a relevant status message upon successful creation, handling potential errors for invalid requests or conflicts.

        Args:
            policy_name (string): The name for the retention policy Example: 'Some Policy Name'.
            description (string): The additional text description of the retention policy. Example: 'Policy to retain all reports for at least one month'.
            policy_type (string): The type of the retention policy. A retention
        policy type can either be `finite`, where a
        specific amount of time to retain the content is known
        upfront, or `indefinite`, where the amount of time
        to retain the content is still unknown. Example: 'finite'.
            disposition_action (string): The disposition action of the retention policy.
        `permanently_delete` deletes the content
        retained by the policy permanently.
        `remove_retention` lifts retention policy
        from the content, allowing it to be deleted
        by users once the retention policy has expired. Example: 'permanently_delete'.
            retention_length (string): The length of the retention policy. This value
        specifies the duration in days that the retention
        policy will be active for after being assigned to
        content.  If the policy has a `policy_type` of
        `indefinite`, the `retention_length` will also be
        `indefinite`. Example: '365'.
            retention_type (string): Specifies the retention type:

        * `modifiable`: You can modify the retention policy. For example,
        you can add or remove folders, shorten or lengthen
        the policy duration, or delete the assignment.
        Use this type if your retention policy
        is not related to any regulatory purposes.

        * `non_modifiable`: You can modify the retention policy
        only in a limited way: add a folder, lengthen the duration,
        retire the policy, change the disposition action
        or notification settings. You cannot perform other actions,
        such as deleting the assignment or shortening the
        policy duration. Use this type to ensure
        compliance with regulatory retention policies. Example: 'modifiable'.
            can_owner_extend_retention (boolean): Whether the owner of a file will be allowed to
        extend the retention. Example: 'True'.
            are_owners_notified (boolean): Whether owner and co-owners of a file are notified
        when the policy nears expiration. Example: 'True'.
            custom_notification_recipients (array): A list of users notified when
        the retention policy duration is about to end.

        Returns:
            dict[str, Any]: Returns a new retention policy object.

        Tags:
            Retention policies
        """
        request_body = {
            'policy_name': policy_name,
            'description': description,
            'policy_type': policy_type,
            'disposition_action': disposition_action,
            'retention_length': retention_length,
            'retention_type': retention_type,
            'can_owner_extend_retention': can_owner_extend_retention,
            'are_owners_notified': are_owners_notified,
            'custom_notification_recipients': custom_notification_recipients,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/retention_policies"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_retention_policies_id(self, retention_policy_id, fields=None) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific data retention policy identified by its retention_policy_id.

        Args:
            retention_policy_id (string): retention_policy_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the retention policy object.

        Tags:
            Retention policies
        """
        if retention_policy_id is None:
            raise ValueError("Missing required parameter 'retention_policy_id'")
        url = f"{self.base_url}/retention_policies/{retention_policy_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_retention_policies_id(self, retention_policy_id, policy_name=None, description=None, disposition_action=None, retention_type=None, retention_length=None, status=None, can_owner_extend_retention=None, are_owners_notified=None, custom_notification_recipients=None) -> dict[str, Any]:
        """
        Updates an existing data retention policy identified by its retention_policy_id to modify how data is retained and purged.

        Args:
            retention_policy_id (string): retention_policy_id
            policy_name (string): The name for the retention policy Example: 'Some Policy Name'.
            description (string): The additional text description of the retention policy. Example: 'Policy to retain all reports for at least one month'.
            disposition_action (string): The disposition action of the retention policy.
        This action can be `permanently_delete`, which
        will cause the content retained by the policy
        to be permanently deleted, or `remove_retention`,
        which will lift the retention policy from the content,
        allowing it to be deleted by users,
        once the retention policy has expired.
        You can use `null` if you don't want to change `disposition_action`. Example: 'permanently_delete'.
            retention_type (string): Specifies the retention type:

        * `modifiable`: You can modify the retention policy. For example,
        you can add or remove folders, shorten or lengthen
        the policy duration, or delete the assignment.
        Use this type if your retention policy
        is not related to any regulatory purposes.
        * `non-modifiable`: You can modify the retention policy
        only in a limited way: add a folder, lengthen the duration,
        retire the policy, change the disposition action
        or notification settings. You cannot perform other actions,
        such as deleting the assignment or shortening the
        policy duration. Use this type to ensure
        compliance with regulatory retention policies.

        When updating a retention policy, you can use
        `non-modifiable` type only. You can convert a
        `modifiable` policy to `non-modifiable`, but
        not the other way around. Example: 'non-modifiable'.
            retention_length (string): The length of the retention policy. This value
        specifies the duration in days that the retention
        policy will be active for after being assigned to
        content.  If the policy has a `policy_type` of
        `indefinite`, the `retention_length` will also be
        `indefinite`. Example: '365'.
            status (string): Used to retire a retention policy.

        If not retiring a policy, do not include this parameter
        or set it to `null`. Example: 'retired'.
            can_owner_extend_retention (boolean): Determines if the owner of items under the policy
        can extend the retention when the original retention
        duration is about to end. Example: 'False'.
            are_owners_notified (boolean): Determines if owners and co-owners of items
        under the policy are notified when
        the retention duration is about to end. Example: 'False'.
            custom_notification_recipients (array): A list of users notified when the retention duration is about to end.

        Returns:
            dict[str, Any]: Returns the updated retention policy object.

        Tags:
            Retention policies
        """
        if retention_policy_id is None:
            raise ValueError("Missing required parameter 'retention_policy_id'")
        request_body = {
            'policy_name': policy_name,
            'description': description,
            'disposition_action': disposition_action,
            'retention_type': retention_type,
            'retention_length': retention_length,
            'status': status,
            'can_owner_extend_retention': can_owner_extend_retention,
            'are_owners_notified': are_owners_notified,
            'custom_notification_recipients': custom_notification_recipients,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/retention_policies/{retention_policy_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_retention_policies_id(self, retention_policy_id) -> Any:
        """
        Deletes a specified retention policy identified by retention_policy_id.

        Args:
            retention_policy_id (string): retention_policy_id

        Returns:
            Any: Returns an empty response when the policy has been deleted.

        Tags:
            Retention policies
        """
        if retention_policy_id is None:
            raise ValueError("Missing required parameter 'retention_policy_id'")
        url = f"{self.base_url}/retention_policies/{retention_policy_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_retention_policies_id_assignments(self, retention_policy_id, type=None, fields=None, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of assignments for a specified retention policy, optionally filtered by type and including specified fields, with support for pagination.

        Args:
            retention_policy_id (string): retention_policy_id
            type (string): The type of the retention policy assignment to retrieve. Example: 'metadata_template'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a list of the retention policy assignments associated with the
        specified retention policy.

        Tags:
            Retention policy assignments
        """
        if retention_policy_id is None:
            raise ValueError("Missing required parameter 'retention_policy_id'")
        url = f"{self.base_url}/retention_policies/{retention_policy_id}/assignments"
        query_params = {k: v for k, v in [('type', type), ('fields', fields), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_retention_policy_assignments(self, policy_id=None, assign_to=None, filter_fields=None, start_date_field=None) -> dict[str, Any]:
        """
        Creates a new retention policy assignment using the "POST" method, specifying rules for retaining files based on folders or metadata, and returns a status message upon successful creation.

        Args:
            policy_id (string): The ID of the retention policy to assign Example: '173463'.
            assign_to (object): The item to assign the policy to
            filter_fields (array): If the `assign_to` type is `metadata_template`,
        then optionally add the `filter_fields` parameter which will
        require an array of objects with a field entry and a value entry.
        Currently only one object of `field` and `value` is supported.
            start_date_field (string): The date the retention policy assignment begins.

        If the `assigned_to` type is `metadata_template`,
        this field can be a date field's metadata attribute key id. Example: 'upload_date'.

        Returns:
            dict[str, Any]: Returns a new retention policy assignment object.

        Tags:
            Retention policy assignments
        """
        request_body = {
            'policy_id': policy_id,
            'assign_to': assign_to,
            'filter_fields': filter_fields,
            'start_date_field': start_date_field,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/retention_policy_assignments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_retention_policy_assignments_id(self, retention_policy_assignment_id, fields=None) -> dict[str, Any]:
        """
        Retrieves the details of a specific retention policy assignment identified by the retention_policy_assignment_id.

        Args:
            retention_policy_assignment_id (string): retention_policy_assignment_id
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the retention policy assignment object.

        Tags:
            Retention policy assignments
        """
        if retention_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'retention_policy_assignment_id'")
        url = f"{self.base_url}/retention_policy_assignments/{retention_policy_assignment_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_retention_policy_assignments_id(self, retention_policy_assignment_id) -> Any:
        """
        Deletes a retention policy assignment by ID using the DELETE method, removing the specified rule that retains files based on predefined conditions.

        Args:
            retention_policy_assignment_id (string): retention_policy_assignment_id

        Returns:
            Any: Returns an empty response when the policy assignment
        is successfully deleted.

        Tags:
            Retention policy assignments
        """
        if retention_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'retention_policy_assignment_id'")
        url = f"{self.base_url}/retention_policy_assignments/{retention_policy_assignment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_retention_policy_assignments_id_files_under_retention(self, retention_policy_assignment_id, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of files currently under retention for a specified retention policy assignment.

        Args:
            retention_policy_assignment_id (string): retention_policy_assignment_id
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a list of files under retention that are associated with the
        specified retention policy assignment.

        Tags:
            Retention policy assignments
        """
        if retention_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'retention_policy_assignment_id'")
        url = f"{self.base_url}/retention_policy_assignments/{retention_policy_assignment_id}/files_under_retention"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_retention_policy_assignments_id_file_versions_under_retention(self, retention_policy_assignment_id, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of file versions that are under retention, associated with a specified retention policy assignment, allowing for pagination via query parameters.

        Args:
            retention_policy_assignment_id (string): retention_policy_assignment_id
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a list of file versions under retention that are associated with
        the specified retention policy assignment.

        Tags:
            Retention policy assignments
        """
        if retention_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'retention_policy_assignment_id'")
        url = f"{self.base_url}/retention_policy_assignments/{retention_policy_assignment_id}/file_versions_under_retention"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_legal_hold_policies(self, policy_name=None, fields=None, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of legal hold policies filtered by optional parameters such as policy name, fields, pagination marker, and limit.

        Args:
            policy_name (string): Limits results to policies for which the names start with
        this search term. This is a case-insensitive prefix. Example: 'Sales Policy'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a list of legal hold policies.

        Tags:
            Legal hold policies
        """
        url = f"{self.base_url}/legal_hold_policies"
        query_params = {k: v for k, v in [('policy_name', policy_name), ('fields', fields), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_legal_hold_policies(self, policy_name=None, description=None, filter_started_at=None, filter_ended_at=None, is_ongoing=None) -> dict[str, Any]:
        """
        Creates a new Legal Hold policy that can include specified restrictions to preserve relevant data for compliance or litigation purposes.

        Args:
            policy_name (string): The name of the policy. Example: 'Sales Policy'.
            description (string): A description for the policy. Example: 'A custom policy for the sales team'.
            filter_started_at (string): The filter start date.

        When this policy is applied using a `custodian` legal
        hold assignments, it will only apply to file versions
        created or uploaded inside of the
        date range. Other assignment types, such as folders and
        files, will ignore the date filter.

        Required if `is_ongoing` is set to `false`. Example: '2012-12-12T10:53:43-08:00'.
            filter_ended_at (string): The filter end date.

        When this policy is applied using a `custodian` legal
        hold assignments, it will only apply to file versions
        created or uploaded inside of the
        date range. Other assignment types, such as folders and
        files, will ignore the date filter.

        Required if `is_ongoing` is set to `false`. Example: '2012-12-18T10:53:43-08:00'.
            is_ongoing (boolean): Whether new assignments under this policy should
        continue applying to files even after initialization.

        When this policy is applied using a legal hold assignment,
        it will continue applying the policy to any new file versions
        even after it has been applied.

        For example, if a legal hold assignment is placed on a user
        today, and that user uploads a file tomorrow, that file will
        get held. This will continue until the policy is retired.

        Required if no filter dates are set. Example: 'True'.

        Returns:
            dict[str, Any]: Returns a new legal hold policy object.

        Tags:
            Legal hold policies
        """
        request_body = {
            'policy_name': policy_name,
            'description': description,
            'filter_started_at': filter_started_at,
            'filter_ended_at': filter_ended_at,
            'is_ongoing': is_ongoing,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/legal_hold_policies"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_legal_hold_policies_id(self, legal_hold_policy_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific legal hold policy identified by its legal_hold_policy_id.

        Args:
            legal_hold_policy_id (string): legal_hold_policy_id

        Returns:
            dict[str, Any]: Returns a legal hold policy object.

        Tags:
            Legal hold policies
        """
        if legal_hold_policy_id is None:
            raise ValueError("Missing required parameter 'legal_hold_policy_id'")
        url = f"{self.base_url}/legal_hold_policies/{legal_hold_policy_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_legal_hold_policies_id(self, legal_hold_policy_id, policy_name=None, description=None, release_notes=None) -> dict[str, Any]:
        """
        Updates the details of an existing legal hold policy identified by the legal_hold_policy_id.

        Args:
            legal_hold_policy_id (string): legal_hold_policy_id
            policy_name (string): The name of the policy. Example: 'Sales Policy'.
            description (string): A description for the policy. Example: 'A custom policy for the sales team'.
            release_notes (string): Notes around why the policy was released. Example: 'Required for GDPR'.

        Returns:
            dict[str, Any]: Returns a new legal hold policy object.

        Tags:
            Legal hold policies
        """
        if legal_hold_policy_id is None:
            raise ValueError("Missing required parameter 'legal_hold_policy_id'")
        request_body = {
            'policy_name': policy_name,
            'description': description,
            'release_notes': release_notes,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/legal_hold_policies/{legal_hold_policy_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_legal_hold_policies_id(self, legal_hold_policy_id) -> Any:
        """
        Deletes an existing legal hold policy asynchronously by its ID, initiating removal without immediate full deletion.

        Args:
            legal_hold_policy_id (string): legal_hold_policy_id

        Returns:
            Any: A blank response is returned if the policy was
        successfully deleted.

        Tags:
            Legal hold policies
        """
        if legal_hold_policy_id is None:
            raise ValueError("Missing required parameter 'legal_hold_policy_id'")
        url = f"{self.base_url}/legal_hold_policies/{legal_hold_policy_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_legal_hold_policy_assignments(self, policy_id, assign_to_type=None, assign_to_id=None, marker=None, limit=None, fields=None) -> dict[str, Any]:
        """
        Retrieves legal hold policy assignments based on specified parameters like policy ID, assignment type, and ID, allowing for pagination and customizable field selection.

        Args:
            policy_id (string): The ID of the legal hold policy Example: '324432'.
            assign_to_type (string): Filters the results by the type of item the
        policy was applied to. Example: 'file'.
            assign_to_id (string): Filters the results by the ID of item the
        policy was applied to. Example: '1234323'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns a list of legal hold policy assignments.

        Tags:
            Legal hold policy assignments
        """
        url = f"{self.base_url}/legal_hold_policy_assignments"
        query_params = {k: v for k, v in [('policy_id', policy_id), ('assign_to_type', assign_to_type), ('assign_to_id', assign_to_id), ('marker', marker), ('limit', limit), ('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_legal_hold_policy_assignments(self, policy_id=None, assign_to=None) -> dict[str, Any]:
        """
        Creates a legal hold policy assignment that places a hold on specified users, folders, files, or file versions to preserve data for legal purposes.

        Args:
            policy_id (string): The ID of the policy to assign. Example: '123244'.
            assign_to (object): The item to assign the policy to

        Returns:
            dict[str, Any]: Returns a new legal hold policy assignment.

        Tags:
            Legal hold policy assignments
        """
        request_body = {
            'policy_id': policy_id,
            'assign_to': assign_to,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/legal_hold_policy_assignments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_legal_hold_policy_assignments_id(self, legal_hold_policy_assignment_id) -> dict[str, Any]:
        """
        Retrieves the details of a specific legal hold policy assignment by its ID.

        Args:
            legal_hold_policy_assignment_id (string): legal_hold_policy_assignment_id

        Returns:
            dict[str, Any]: Returns a legal hold policy object.

        Tags:
            Legal hold policy assignments
        """
        if legal_hold_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'legal_hold_policy_assignment_id'")
        url = f"{self.base_url}/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_legal_hold_policy_assignments_id(self, legal_hold_policy_assignment_id) -> Any:
        """
        Deletes a legal hold policy assignment by its ID, initiating an asynchronous removal of the hold from the assigned item.

        Args:
            legal_hold_policy_assignment_id (string): legal_hold_policy_assignment_id

        Returns:
            Any: A blank response is returned if the assignment was
        successfully deleted.

        Tags:
            Legal hold policy assignments
        """
        if legal_hold_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'legal_hold_policy_assignment_id'")
        url = f"{self.base_url}/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_legal_hold_policy_assignments_id_files_on_hold(self, legal_hold_policy_assignment_id, marker=None, limit=None, fields=None) -> dict[str, Any]:
        """
        Retrieves the list of files currently on hold under a specific legal hold policy assignment.

        Args:
            legal_hold_policy_assignment_id (string): legal_hold_policy_assignment_id
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the list of current file versions held under legal hold for a
        specific legal hold policy assignment.

        Tags:
            Legal hold policy assignments
        """
        if legal_hold_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'legal_hold_policy_assignment_id'")
        url = f"{self.base_url}/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}/files_on_hold"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit), ('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_version_retentions(self, file_id=None, file_version_id=None, policy_id=None, disposition_action=None, disposition_before=None, disposition_after=None, limit=None, marker=None) -> dict[str, Any]:
        """
        Retrieves a list of file version retentions filtered by query parameters such as file ID, version ID, policy ID, disposition action, and date range.

        Args:
            file_id (string): Filters results by files with this ID. Example: '43123123'.
            file_version_id (string): Filters results by file versions with this ID. Example: '1'.
            policy_id (string): Filters results by the retention policy with this ID. Example: '982312'.
            disposition_action (string): Filters results by the retention policy with this disposition
        action. Example: 'permanently_delete'.
            disposition_before (string): Filters results by files that will have their disposition
        come into effect before this date. Example: '2012-12-12T10:53:43-08:00'.
            disposition_after (string): Filters results by files that will have their disposition
        come into effect after this date. Example: '2012-12-19T10:34:23-08:00'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.

        Returns:
            dict[str, Any]: Returns a list of all file version retentions for the enterprise.

        Tags:
            File version retentions
        """
        url = f"{self.base_url}/file_version_retentions"
        query_params = {k: v for k, v in [('file_id', file_id), ('file_version_id', file_version_id), ('policy_id', policy_id), ('disposition_action', disposition_action), ('disposition_before', disposition_before), ('disposition_after', disposition_after), ('limit', limit), ('marker', marker)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_legal_hold_policy_assignments_id_file_versions_on_hold(self, legal_hold_policy_assignment_id, marker=None, limit=None, fields=None) -> dict[str, Any]:
        """
        Retrieves a list of file versions currently on hold under a specified legal hold policy assignment.

        Args:
            legal_hold_policy_assignment_id (string): legal_hold_policy_assignment_id
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".

        Returns:
            dict[str, Any]: Returns the list of previous file versions held under legal hold for a
        specific legal hold policy assignment.

        Tags:
            Legal hold policy assignments
        """
        if legal_hold_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'legal_hold_policy_assignment_id'")
        url = f"{self.base_url}/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}/file_versions_on_hold"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit), ('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_version_retentions_id(self, file_version_retention_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific file version retention by its ID.

        Args:
            file_version_retention_id (string): file_version_retention_id

        Returns:
            dict[str, Any]: Returns a file version retention object.

        Tags:
            File version retentions
        """
        if file_version_retention_id is None:
            raise ValueError("Missing required parameter 'file_version_retention_id'")
        url = f"{self.base_url}/file_version_retentions/{file_version_retention_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_version_legal_holds_id(self, file_version_legal_hold_id) -> dict[str, Any]:
        """
        Retrieves details of a specific file version legal hold using its unique identifier.

        Args:
            file_version_legal_hold_id (string): file_version_legal_hold_id

        Returns:
            dict[str, Any]: Returns the legal hold policy assignments for the file version.

        Tags:
            File version legal holds
        """
        if file_version_legal_hold_id is None:
            raise ValueError("Missing required parameter 'file_version_legal_hold_id'")
        url = f"{self.base_url}/file_version_legal_holds/{file_version_legal_hold_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_version_legal_holds(self, policy_id, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of legal holds applied to file versions, supporting pagination and filtering by policy ID.

        Args:
            policy_id (string): The ID of the legal hold policy to get the file version legal
        holds for. Example: '133870'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns the list of file version legal holds for a specific legal
        hold policy.

        Tags:
            File version legal holds
        """
        url = f"{self.base_url}/file_version_legal_holds"
        query_params = {k: v for k, v in [('policy_id', policy_id), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barriers_id(self, shield_information_barrier_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific shield information barrier identified by its ID.

        Args:
            shield_information_barrier_id (string): shield_information_barrier_id

        Returns:
            dict[str, Any]: Returns the shield information barrier object.

        Tags:
            Shield information barriers
        """
        if shield_information_barrier_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_id'")
        url = f"{self.base_url}/shield_information_barriers/{shield_information_barrier_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_shield_information_barriers_change_status(self, id=None, status=None) -> dict[str, Any]:
        """
        Changes the status of a specified shield information barrier using the POST method.

        Args:
            id (string): The ID of the shield information barrier. Example: '1910967'.
            status (string): The desired status for the shield information barrier. Example: 'pending'.

        Returns:
            dict[str, Any]: Returns the updated shield information barrier object.

        Tags:
            Shield information barriers
        """
        request_body = {
            'id': id,
            'status': status,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/shield_information_barriers/change_status"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barriers(self, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of shield information barriers using the GET method, allowing users to manage and access restrictions between user segments in Box, with optional parameters to control pagination via "marker" and "limit".

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a paginated list of
        shield information barrier objects,
        empty list if currently no barrier.

        Tags:
            Shield information barriers
        """
        url = f"{self.base_url}/shield_information_barriers"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_shield_information_barriers(self, enterprise=None) -> dict[str, Any]:
        """
        Creates a shield information barrier to separate individuals or groups within the same firm, preventing the exchange of confidential information between them using the Box API.

        Args:
            enterprise (string): The `type` and `id` of enterprise this barrier is under.

        Returns:
            dict[str, Any]: Returns a new shield information barrier object.

        Tags:
            Shield information barriers
        """
        request_body = {
            'enterprise': enterprise,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/shield_information_barriers"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barrier_reports(self, shield_information_barrier_id, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of shield information barrier reports based on specified query parameters.

        Args:
            shield_information_barrier_id (string): The ID of the shield information barrier. Example: '1910967'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a paginated list of shield information barrier report objects.

        Tags:
            Shield information barrier reports
        """
        url = f"{self.base_url}/shield_information_barrier_reports"
        query_params = {k: v for k, v in [('shield_information_barrier_id', shield_information_barrier_id), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_shield_information_barrier_reports(self, shield_information_barrier=None) -> dict[str, Any]:
        """
        Creates a new shield information barrier report to track and manage data access restrictions between user segments.

        Args:
            shield_information_barrier (object): A base representation of a
        shield information barrier object

        Returns:
            dict[str, Any]: Returns the shield information barrier report information object.

        Tags:
            Shield information barrier reports
        """
        request_body = {
            'shield_information_barrier': shield_information_barrier,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/shield_information_barrier_reports"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barrier_reports_id(self, shield_information_barrier_report_id) -> dict[str, Any]:
        """
        Retrieves a specific shield information barrier report by its ID using the GET method.

        Args:
            shield_information_barrier_report_id (string): shield_information_barrier_report_id

        Returns:
            dict[str, Any]: Returns the  shield information barrier report object.

        Tags:
            Shield information barrier reports
        """
        if shield_information_barrier_report_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_report_id'")
        url = f"{self.base_url}/shield_information_barrier_reports/{shield_information_barrier_report_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barrier_segments_id(self, shield_information_barrier_segment_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific shield information barrier segment identified by its ID.

        Args:
            shield_information_barrier_segment_id (string): shield_information_barrier_segment_id

        Returns:
            dict[str, Any]: Returns the shield information barrier segment object.

        Tags:
            Shield information barrier segments
        """
        if shield_information_barrier_segment_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_segment_id'")
        url = f"{self.base_url}/shield_information_barrier_segments/{shield_information_barrier_segment_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_shield_information_barrier_segments_id(self, shield_information_barrier_segment_id) -> Any:
        """
        Deletes a specific information barrier segment identified by its ID using the Box API.

        Args:
            shield_information_barrier_segment_id (string): shield_information_barrier_segment_id

        Returns:
            Any: Empty body in response

        Tags:
            Shield information barrier segments
        """
        if shield_information_barrier_segment_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_segment_id'")
        url = f"{self.base_url}/shield_information_barrier_segments/{shield_information_barrier_segment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_shield_information_barrier_segments_id(self, shield_information_barrier_segment_id, name=None, description=None) -> dict[str, Any]:
        """
        Updates the properties of a specified shield information barrier segment identified by its ID.

        Args:
            shield_information_barrier_segment_id (string): shield_information_barrier_segment_id
            name (string): The updated name for the shield information barrier segment. Example: 'Investment Banking'.
            description (string): The updated description for
        the shield information barrier segment. Example: "'Corporate division that engages in advisory_based\nfinancial transactions on behalf of individuals,\ncorporations, and governments.'".

        Returns:
            dict[str, Any]: Returns the updated shield information barrier segment object.

        Tags:
            Shield information barrier segments
        """
        if shield_information_barrier_segment_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_segment_id'")
        request_body = {
            'name': name,
            'description': description,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/shield_information_barrier_segments/{shield_information_barrier_segment_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barrier_segments(self, shield_information_barrier_id, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of shield information barrier segments filtered by the specified information barrier ID, with optional pagination parameters.

        Args:
            shield_information_barrier_id (string): The ID of the shield information barrier. Example: '1910967'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a paginated list of shield information barrier segment objects.

        Tags:
            Shield information barrier segments
        """
        url = f"{self.base_url}/shield_information_barrier_segments"
        query_params = {k: v for k, v in [('shield_information_barrier_id', shield_information_barrier_id), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_shield_information_barrier_segments(self, shield_information_barrier=None, name=None, description=None) -> dict[str, Any]:
        """
        Creates a new shield information barrier segment to define a restricted communication boundary between user groups within an organization.

        Args:
            shield_information_barrier (object): A base representation of a
        shield information barrier object
            name (string): Name of the shield information barrier segment Example: 'Investment Banking'.
            description (string): Description of the shield information barrier segment Example: "'Corporate division that engages in\n advisory_based financial\ntransactions on behalf of individuals,\ncorporations, and governments.'".

        Returns:
            dict[str, Any]: Returns a new shield information barrier segment object.

        Tags:
            Shield information barrier segments
        """
        request_body = {
            'shield_information_barrier': shield_information_barrier,
            'name': name,
            'description': description,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/shield_information_barrier_segments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barrier_segment_members_id(self, shield_information_barrier_segment_member_id) -> dict[str, Any]:
        """
        Retrieves a specific shield information barrier segment member by its ID using the GET method.

        Args:
            shield_information_barrier_segment_member_id (string): shield_information_barrier_segment_member_id

        Returns:
            dict[str, Any]: Returns the shield information barrier segment member object.

        Tags:
            Shield information barrier segment members
        """
        if shield_information_barrier_segment_member_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_segment_member_id'")
        url = f"{self.base_url}/shield_information_barrier_segment_members/{shield_information_barrier_segment_member_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_shield_information_barrier_segment_members_id(self, shield_information_barrier_segment_member_id) -> Any:
        """
        Deletes a shield information barrier segment member identified by the given ID.

        Args:
            shield_information_barrier_segment_member_id (string): shield_information_barrier_segment_member_id

        Returns:
            Any: Returns an empty response if the
        segment member was deleted successfully.

        Tags:
            Shield information barrier segment members
        """
        if shield_information_barrier_segment_member_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_segment_member_id'")
        url = f"{self.base_url}/shield_information_barrier_segment_members/{shield_information_barrier_segment_member_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barrier_segment_members(self, shield_information_barrier_segment_id, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of members for a specified shield information barrier segment using the Box API, allowing for pagination with optional marker and limit parameters.

        Args:
            shield_information_barrier_segment_id (string): The ID of the shield information barrier segment. Example: '3423'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a paginated list of
        shield information barrier segment member objects.

        Tags:
            Shield information barrier segment members
        """
        url = f"{self.base_url}/shield_information_barrier_segment_members"
        query_params = {k: v for k, v in [('shield_information_barrier_segment_id', shield_information_barrier_segment_id), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_shield_information_barrier_segment_members(self, type=None, shield_information_barrier=None, shield_information_barrier_segment=None, user=None) -> dict[str, Any]:
        """
        Creates a new shield information barrier segment member using the Box API and returns a status message indicating the result of the operation.

        Args:
            type (string): -| A type of the shield barrier segment member. Example: 'shield_information_barrier_segment_member'.
            shield_information_barrier (object): A base representation of a
        shield information barrier object
            shield_information_barrier_segment (object): The `type` and `id` of the
        requested shield information barrier segment.
            user (string): User to which restriction will be applied.

        Returns:
            dict[str, Any]: Returns a new shield information barrier segment member object.

        Tags:
            Shield information barrier segment members
        """
        request_body = {
            'type': type,
            'shield_information_barrier': shield_information_barrier,
            'shield_information_barrier_segment': shield_information_barrier_segment,
            'user': user,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/shield_information_barrier_segment_members"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barrier_segment_restrictions_id(self, shield_information_barrier_segment_restriction_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific shield information barrier segment restriction by its ID.

        Args:
            shield_information_barrier_segment_restriction_id (string): shield_information_barrier_segment_restriction_id

        Returns:
            dict[str, Any]: Returns the shield information barrier segment
        restriction object.

        Tags:
            Shield information barrier segment restrictions
        """
        if shield_information_barrier_segment_restriction_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_segment_restriction_id'")
        url = f"{self.base_url}/shield_information_barrier_segment_restrictions/{shield_information_barrier_segment_restriction_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_shield_information_barrier_segment_restrictions_id(self, shield_information_barrier_segment_restriction_id) -> Any:
        """
        Deletes a specified shield information barrier segment restriction by its ID, removing the associated restriction from the system.

        Args:
            shield_information_barrier_segment_restriction_id (string): shield_information_barrier_segment_restriction_id

        Returns:
            Any: Empty body in response

        Tags:
            Shield information barrier segment restrictions
        """
        if shield_information_barrier_segment_restriction_id is None:
            raise ValueError("Missing required parameter 'shield_information_barrier_segment_restriction_id'")
        url = f"{self.base_url}/shield_information_barrier_segment_restrictions/{shield_information_barrier_segment_restriction_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_shield_information_barrier_segment_restrictions(self, shield_information_barrier_segment_id, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of segment restrictions for an information barrier segment specified by the `shield_information_barrier_segment_id` using the Box API.

        Args:
            shield_information_barrier_segment_id (string): The ID of the shield information barrier segment. Example: '3423'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a paginated list of
        shield information barrier segment restriction objects.

        Tags:
            Shield information barrier segment restrictions
        """
        url = f"{self.base_url}/shield_information_barrier_segment_restrictions"
        query_params = {k: v for k, v in [('shield_information_barrier_segment_id', shield_information_barrier_segment_id), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_shield_information_barrier_segment_restrictions(self, type=None, shield_information_barrier=None, shield_information_barrier_segment=None, restricted_segment=None) -> dict[str, Any]:
        """
        Creates a new shield information barrier segment restriction to control data access between defined segments.

        Args:
            type (string): The type of the shield barrier segment
        restriction for this member. Example: 'shield_information_barrier_segment_restriction'.
            shield_information_barrier (object): A base representation of a
        shield information barrier object
            shield_information_barrier_segment (object): The `type` and `id` of the requested
        shield information barrier segment.
            restricted_segment (object): The `type` and `id` of the restricted
        shield information barrier segment.

        Returns:
            dict[str, Any]: Returns the newly created Shield
        Information Barrier Segment Restriction object.

        Tags:
            Shield information barrier segment restrictions
        """
        request_body = {
            'type': type,
            'shield_information_barrier': shield_information_barrier,
            'shield_information_barrier_segment': shield_information_barrier_segment,
            'restricted_segment': restricted_segment,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/shield_information_barrier_segment_restrictions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_device_pinners_id(self, device_pinner_id) -> dict[str, Any]:
        """
        Retrieves details for a specific device pinner using its unique identifier.

        Args:
            device_pinner_id (string): device_pinner_id

        Returns:
            dict[str, Any]: Returns information about a single device pin.

        Tags:
            Device pinners
        """
        if device_pinner_id is None:
            raise ValueError("Missing required parameter 'device_pinner_id'")
        url = f"{self.base_url}/device_pinners/{device_pinner_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_device_pinners_id(self, device_pinner_id) -> Any:
        """
        Deletes a device pinner by ID using the DELETE method, identified by the path parameter "device_pinner_id".

        Args:
            device_pinner_id (string): device_pinner_id

        Returns:
            Any: Returns an empty response when the pin has been deleted.

        Tags:
            Device pinners
        """
        if device_pinner_id is None:
            raise ValueError("Missing required parameter 'device_pinner_id'")
        url = f"{self.base_url}/device_pinners/{device_pinner_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_enterprises_id_device_pinners(self, enterprise_id, marker=None, limit=None, direction=None) -> dict[str, Any]:
        """
        Retrieves a list of all device pins within a specified enterprise to manage and inspect devices authorized to access Box applications.

        Args:
            enterprise_id (string): enterprise_id
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            direction (string): The direction to sort results in. This can be either in alphabetical ascending
        (`ASC`) or descending (`DESC`) order. Example: 'ASC'.

        Returns:
            dict[str, Any]: Returns a list of device pins for a given enterprise.

        Tags:
            Device pinners
        """
        if enterprise_id is None:
            raise ValueError("Missing required parameter 'enterprise_id'")
        url = f"{self.base_url}/enterprises/{enterprise_id}/device_pinners"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit), ('direction', direction)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_terms_of_services(self, tos_type=None) -> dict[str, Any]:
        """
        Retrieves terms of service details based on the specified type using the GET method at the "/terms_of_services" path, with the type of terms of service passed as a query parameter named "tos_type."

        Args:
            tos_type (string): Limits the results to the terms of service of the given type. Example: 'managed'.

        Returns:
            dict[str, Any]: Returns a collection of terms of service text and settings for the
        enterprise.

        Tags:
            Terms of service
        """
        url = f"{self.base_url}/terms_of_services"
        query_params = {k: v for k, v in [('tos_type', tos_type)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_terms_of_services(self, status=None, tos_type=None, text=None) -> dict[str, Any]:
        """
        Submits terms of service data to the server using the POST method and returns a response indicating the result.

        Args:
            status (string): Whether this terms of service is active. Example: 'enabled'.
            tos_type (string): The type of user to set the terms of
        service for. Example: 'managed'.
            text (string): The terms of service text to display to users.

        The text can be set to empty if the `status` is set to `disabled`. Example: 'By collaborating on this file you are accepting...'.

        Returns:
            dict[str, Any]: Returns a new task object

        Tags:
            Terms of service
        """
        request_body = {
            'status': status,
            'tos_type': tos_type,
            'text': text,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/terms_of_services"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_terms_of_services_id(self, terms_of_service_id) -> dict[str, Any]:
        """
        Retrieves the details of a specific Terms of Service identified by the provided terms_of_service_id.

        Args:
            terms_of_service_id (string): terms_of_service_id

        Returns:
            dict[str, Any]: Returns a terms of service object.

        Tags:
            Terms of service
        """
        if terms_of_service_id is None:
            raise ValueError("Missing required parameter 'terms_of_service_id'")
        url = f"{self.base_url}/terms_of_services/{terms_of_service_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_terms_of_services_id(self, terms_of_service_id, status=None, text=None) -> dict[str, Any]:
        """
        Updates the terms of service identified by the given terms_of_service_id with new information.

        Args:
            terms_of_service_id (string): terms_of_service_id
            status (string): Whether this terms of service is active. Example: 'enabled'.
            text (string): The terms of service text to display to users.

        The text can be set to empty if the `status` is set to `disabled`. Example: 'By collaborating on this file you are accepting...'.

        Returns:
            dict[str, Any]: Returns an updated terms of service object.

        Tags:
            Terms of service
        """
        if terms_of_service_id is None:
            raise ValueError("Missing required parameter 'terms_of_service_id'")
        request_body = {
            'status': status,
            'text': text,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/terms_of_services/{terms_of_service_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_terms_of_service_user_statuses(self, tos_id, user_id=None) -> dict[str, Any]:
        """
        Retrieves a list of user statuses for a specified terms of service, including whether users have accepted the terms and when, using query parameters to filter by terms of service ID and user ID.

        Args:
            tos_id (string): The ID of the terms of service. Example: '324234'.
            user_id (string): Limits results to the given user ID. Example: '123334'.

        Returns:
            dict[str, Any]: Returns a list of terms of service statuses.

        Tags:
            Terms of service user statuses
        """
        url = f"{self.base_url}/terms_of_service_user_statuses"
        query_params = {k: v for k, v in [('tos_id', tos_id), ('user_id', user_id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_terms_of_service_user_statuses(self, tos=None, user=None, is_accepted=None) -> dict[str, Any]:
        """
        Creates a new record tracking the acceptance status of a specific user for a terms of service agreement and returns a confirmation upon success.

        Args:
            tos (object): The terms of service to set the status for.
            user (object): The user to set the status for.
            is_accepted (boolean): Whether the user has accepted the terms. Example: 'True'.

        Returns:
            dict[str, Any]: Returns a terms of service status object.

        Tags:
            Terms of service user statuses
        """
        request_body = {
            'tos': tos,
            'user': user,
            'is_accepted': is_accepted,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/terms_of_service_user_statuses"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_terms_of_service_user_statuses_id(self, terms_of_service_user_status_id, is_accepted=None) -> dict[str, Any]:
        """
        Updates the status of a user's acceptance for a specific Terms of Service using the given user status ID.

        Args:
            terms_of_service_user_status_id (string): terms_of_service_user_status_id
            is_accepted (boolean): Whether the user has accepted the terms. Example: 'True'.

        Returns:
            dict[str, Any]: Returns the updated terms of service status object.

        Tags:
            Terms of service user statuses
        """
        if terms_of_service_user_status_id is None:
            raise ValueError("Missing required parameter 'terms_of_service_user_status_id'")
        request_body = {
            'is_accepted': is_accepted,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/terms_of_service_user_statuses/{terms_of_service_user_status_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collaboration_whitelist_entries(self, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of collaboration whitelist entries that specify allowed email domains for collaboration within the enterprise.

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of domains that are allowed for collaboration.

        Tags:
            Domain restrictions for collaborations
        """
        url = f"{self.base_url}/collaboration_whitelist_entries"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_collaboration_whitelist_entries(self, domain=None, direction=None) -> dict[str, Any]:
        """
        Creates a collaboration whitelist entry to specify allowed domains and directions for repository collaboration.

        Args:
            domain (string): The domain to add to the list of allowed domains. Example: 'example.com'.
            direction (string): The direction in which to allow collaborations. Example: 'inbound'.

        Returns:
            dict[str, Any]: Returns a new entry on the list of allowed domains.

        Tags:
            Domain restrictions for collaborations
        """
        request_body = {
            'domain': domain,
            'direction': direction,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/collaboration_whitelist_entries"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collaboration_whitelist_entries_id(self, collaboration_whitelist_entry_id) -> dict[str, Any]:
        """
        Retrieves information about a specific collaboration whitelist entry identified by its ID.

        Args:
            collaboration_whitelist_entry_id (string): collaboration_whitelist_entry_id

        Returns:
            dict[str, Any]: Returns an entry on the list of allowed domains.

        Tags:
            Domain restrictions for collaborations
        """
        if collaboration_whitelist_entry_id is None:
            raise ValueError("Missing required parameter 'collaboration_whitelist_entry_id'")
        url = f"{self.base_url}/collaboration_whitelist_entries/{collaboration_whitelist_entry_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_collaboration_whitelist_entries_id(self, collaboration_whitelist_entry_id) -> Any:
        """
        Deletes a specific collaboration whitelist entry identified by its ID using the DELETE method, returning a status code indicating successful removal.

        Args:
            collaboration_whitelist_entry_id (string): collaboration_whitelist_entry_id

        Returns:
            Any: A blank response is returned if the entry was
        successfully deleted.

        Tags:
            Domain restrictions for collaborations
        """
        if collaboration_whitelist_entry_id is None:
            raise ValueError("Missing required parameter 'collaboration_whitelist_entry_id'")
        url = f"{self.base_url}/collaboration_whitelist_entries/{collaboration_whitelist_entry_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collaboration_whitelist_exempt_targets(self, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of users who are exempt from the collaboration whitelist using the Box API.

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of user exemptions.

        Tags:
            Domain restrictions (User exemptions)
        """
        url = f"{self.base_url}/collaboration_whitelist_exempt_targets"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_collaboration_whitelist_exempt_targets(self, user=None) -> dict[str, Any]:
        """
        Creates a new collaboration whitelist exempt target, allowing specified users or entities to bypass collaboration whitelist domain restrictions.

        Args:
            user (object): The user to exempt.

        Returns:
            dict[str, Any]: Returns a new exemption entry.

        Tags:
            Domain restrictions (User exemptions)
        """
        request_body = {
            'user': user,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/collaboration_whitelist_exempt_targets"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_collaboration_whitelist_exempt_targets_id(self, collaboration_whitelist_exempt_target_id) -> dict[str, Any]:
        """
        Retrieves details of a specific collaboration whitelist exempt target identified by its ID.

        Args:
            collaboration_whitelist_exempt_target_id (string): collaboration_whitelist_exempt_target_id

        Returns:
            dict[str, Any]: Returns the user's exempted from the list of collaboration domains.

        Tags:
            Domain restrictions (User exemptions)
        """
        if collaboration_whitelist_exempt_target_id is None:
            raise ValueError("Missing required parameter 'collaboration_whitelist_exempt_target_id'")
        url = f"{self.base_url}/collaboration_whitelist_exempt_targets/{collaboration_whitelist_exempt_target_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_collaboration_whitelist_exempt_targets_id(self, collaboration_whitelist_exempt_target_id) -> Any:
        """
        Removes a specific collaboration whitelist exemption by ID, revoking the target's exemption from domain restrictions using the Box API.

        Args:
            collaboration_whitelist_exempt_target_id (string): collaboration_whitelist_exempt_target_id

        Returns:
            Any: A blank response is returned if the exemption was
        successfully deleted.

        Tags:
            Domain restrictions (User exemptions)
        """
        if collaboration_whitelist_exempt_target_id is None:
            raise ValueError("Missing required parameter 'collaboration_whitelist_exempt_target_id'")
        url = f"{self.base_url}/collaboration_whitelist_exempt_targets/{collaboration_whitelist_exempt_target_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_storage_policies(self, fields=None, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of storage policies with optional filtering, pagination, and field selection parameters.

        Args:
            fields (array): A comma-separated list of attributes to include in the
        response. This can be used to request fields that are
        not normally returned in a standard response. Be aware that specifying this parameter will have the
        effect that none of the standard fields are returned in
        the response unless explicitly specified, instead only
        fields for the mini representation are returned, additional
        to the fields requested. Example: "['id', 'type', 'name']".
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of storage policies.

        Tags:
            Standard and Zones Storage Policies
        """
        url = f"{self.base_url}/storage_policies"
        query_params = {k: v for k, v in [('fields', fields), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_storage_policies_id(self, storage_policy_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific storage policy identified by its storage_policy_id.

        Args:
            storage_policy_id (string): storage_policy_id

        Returns:
            dict[str, Any]: Returns a storage policy object.

        Tags:
            Standard and Zones Storage Policies
        """
        if storage_policy_id is None:
            raise ValueError("Missing required parameter 'storage_policy_id'")
        url = f"{self.base_url}/storage_policies/{storage_policy_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_storage_policy_assignments(self, resolved_for_type, resolved_for_id, marker=None) -> dict[str, Any]:
        """
        Retrieves a list of storage policy assignments with optional pagination and filtering by resolved type and ID.

        Args:
            resolved_for_type (string): The target type to return assignments for Example: 'user'.
            resolved_for_id (string): The ID of the user or enterprise to return assignments for Example: '984322'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.

        Returns:
            dict[str, Any]: Returns a collection of storage policies for
        the enterprise or user.

        Tags:
            Standard and Zones Storage Policy Assignments
        """
        url = f"{self.base_url}/storage_policy_assignments"
        query_params = {k: v for k, v in [('marker', marker), ('resolved_for_type', resolved_for_type), ('resolved_for_id', resolved_for_id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_storage_policy_assignments(self, storage_policy=None, assigned_to=None) -> dict[str, Any]:
        """
        Creates a new storage policy assignment to a user or enterprise.

        Args:
            storage_policy (object): The storage policy to assign to the user or
        enterprise
            assigned_to (object): The user or enterprise to assign the storage
        policy to.

        Returns:
            dict[str, Any]: Returns the new storage policy assignment created.

        Tags:
            Standard and Zones Storage Policy Assignments
        """
        request_body = {
            'storage_policy': storage_policy,
            'assigned_to': assigned_to,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/storage_policy_assignments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_storage_policy_assignments_id(self, storage_policy_assignment_id) -> dict[str, Any]:
        """
        Retrieves details of a specific storage policy assignment identified by its storage_policy_assignment_id.

        Args:
            storage_policy_assignment_id (string): storage_policy_assignment_id

        Returns:
            dict[str, Any]: Returns a storage policy assignment object.

        Tags:
            Standard and Zones Storage Policy Assignments
        """
        if storage_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'storage_policy_assignment_id'")
        url = f"{self.base_url}/storage_policy_assignments/{storage_policy_assignment_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_storage_policy_assignments_id(self, storage_policy_assignment_id, storage_policy=None) -> dict[str, Any]:
        """
        Updates an existing storage policy assignment identified by storage_policy_assignment_id with new settings or configurations.

        Args:
            storage_policy_assignment_id (string): storage_policy_assignment_id
            storage_policy (object): The storage policy to assign to the user or
        enterprise

        Returns:
            dict[str, Any]: Returns an updated storage policy assignment object.

        Tags:
            Standard and Zones Storage Policy Assignments
        """
        if storage_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'storage_policy_assignment_id'")
        request_body = {
            'storage_policy': storage_policy,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/storage_policy_assignments/{storage_policy_assignment_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_storage_policy_assignments_id(self, storage_policy_assignment_id) -> Any:
        """
        Deletes a storage policy assignment identified by its ID, causing the user to inherit the enterprise's default storage policy.

        Args:
            storage_policy_assignment_id (string): storage_policy_assignment_id

        Returns:
            Any: Returns an empty response when the storage policy
        assignment is successfully deleted.

        Tags:
            Standard and Zones Storage Policy Assignments
        """
        if storage_policy_assignment_id is None:
            raise ValueError("Missing required parameter 'storage_policy_assignment_id'")
        url = f"{self.base_url}/storage_policy_assignments/{storage_policy_assignment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_zip_downloads(self, items=None, download_file_name=None) -> dict[str, Any]:
        """
        Creates a downloadable ZIP archive based on the provided input data and initiates the download process.

        Args:
            items (array): A list of items to add to the `zip` archive. These can
        be folders or files.
            download_file_name (string): The optional name of the `zip` archive. This name will be appended by the
        `.zip` file extension, for example `January Financials.zip`. Example: 'January Financials'.

        Returns:
            dict[str, Any]: If the `zip` archive is ready to be downloaded, the API will return a
        response that will include a `download_url`, a `status_url`, as well as
        any conflicts that might have occurred when creating the request.

        Tags:
            Zip Downloads
        """
        request_body = {
            'items': items,
            'download_file_name': download_file_name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/zip_downloads"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_zip_downloads_id_content(self, zip_download_id) -> Any:
        """
        Retrieves the content of a specific zip download identified by the `zip_download_id`.

        Args:
            zip_download_id (string): zip_download_id

        Returns:
            Any: Returns the content of the items requested for this download, formatted as
        a stream of files and folders in a `zip` archive.

        Tags:
            Zip Downloads
        """
        if zip_download_id is None:
            raise ValueError("Missing required parameter 'zip_download_id'")
        url = f"{self.base_url}/zip_downloads/{zip_download_id}/content"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_zip_downloads_id_status(self, zip_download_id) -> dict[str, Any]:
        """
        Retrieves the status of a specific zip download identified by the zip_download_id using the GET method.

        Args:
            zip_download_id (string): zip_download_id

        Returns:
            dict[str, Any]: Returns the status of the `zip` archive that is being downloaded.

        Tags:
            Zip Downloads
        """
        if zip_download_id is None:
            raise ValueError("Missing required parameter 'zip_download_id'")
        url = f"{self.base_url}/zip_downloads/{zip_download_id}/status"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_sign_requests_id_cancel(self, sign_request_id) -> dict[str, Any]:
        """
        Cancels an incomplete sign request using the provided sign request ID, preventing further signatures from being added.

        Args:
            sign_request_id (string): sign_request_id

        Returns:
            dict[str, Any]: Returns a Sign Request object.

        Tags:
            Box Sign requests
        """
        if sign_request_id is None:
            raise ValueError("Missing required parameter 'sign_request_id'")
        url = f"{self.base_url}/sign_requests/{sign_request_id}/cancel"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_sign_requests_id_resend(self, sign_request_id) -> Any:
        """
        Resends a specified sign request identified by sign_request_id and returns a status indicating the outcome.

        Args:
            sign_request_id (string): sign_request_id

        Returns:
            Any: Returns an empty response when the API call was successful.
        The email notifications will be sent asynchronously.

        Tags:
            Box Sign requests
        """
        if sign_request_id is None:
            raise ValueError("Missing required parameter 'sign_request_id'")
        url = f"{self.base_url}/sign_requests/{sign_request_id}/resend"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sign_requests_id(self, sign_request_id) -> dict[str, Any]:
        """
        Retrieves the details of a specific sign request using the provided sign request identifier.

        Args:
            sign_request_id (string): sign_request_id

        Returns:
            dict[str, Any]: Returns a signature request.

        Tags:
            Box Sign requests
        """
        if sign_request_id is None:
            raise ValueError("Missing required parameter 'sign_request_id'")
        url = f"{self.base_url}/sign_requests/{sign_request_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sign_requests(self, marker=None, limit=None, senders=None, shared_requests=None) -> dict[str, Any]:
        """
        Retrieves a list of sign requests filtered by optional parameters such as marker, limit, senders, and shared requests.

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            senders (array): A list of sender emails to filter the signature requests by sender.
        If provided, `shared_requests` must be set to `true`. Example: "['sender1@boxdemo.com', 'sender2@boxdemo.com']".
            shared_requests (boolean): If set to `true`, only includes requests that user is not an owner,
        but user is a collaborator. Collaborator access is determined by the
        user access level of the sign files of the request.
        Default is `false`. Must be set to `true` if `senders` are provided. Example: 'True'.

        Returns:
            dict[str, Any]: Returns a collection of sign requests

        Tags:
            Box Sign requests
        """
        url = f"{self.base_url}/sign_requests"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit), ('senders', senders), ('shared_requests', shared_requests)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_sign_requests(self, is_document_preparation_needed=None, redirect_url=None, declined_redirect_url=None, are_text_signatures_enabled=None, email_subject=None, email_message=None, are_reminders_enabled=None, name=None, prefill_tags=None, days_valid=None, external_id=None, template_id=None, external_system_name=None, source_files=None, signature_color=None, signers=None, parent_folder=None) -> dict[str, Any]:
        """
        Submits data to generate a signed request and returns a confirmation response.

        Args:
            is_document_preparation_needed (boolean): Indicates if the sender should receive a `prepare_url` in the response to complete document preparation using the UI. Example: 'True'.
            redirect_url (string): When specified, the signature request will be redirected to this url when a document is signed. Example: 'https://www.example.com'.
            declined_redirect_url (string): The uri that a signer will be redirected to after declining to sign a document. Example: 'https://declined-redirect.com'.
            are_text_signatures_enabled (boolean): Disables the usage of signatures generated by typing (text). Example: 'True'.
            email_subject (string): Subject of sign request email. This is cleaned by sign request. If this field is not passed, a default subject will be used. Example: 'Sign Request from Acme'.
            email_message (string): Message to include in sign request email. The field is cleaned through sanitization of specific characters. However, some html tags are allowed. Links included in the message are also converted to hyperlinks in the email. The message may contain the following html tags including `a`, `abbr`, `acronym`, `b`, `blockquote`, `code`, `em`, `i`, `ul`, `li`, `ol`, and `strong`. Be aware that when the text to html ratio is too high, the email may end up in spam filters. Custom styles on these tags are not allowed. If this field is not passed, a default message will be used. Example: 'Hello! Please sign the document below'.
            are_reminders_enabled (boolean): Reminds signers to sign a document on day 3, 8, 13 and 18. Reminders are only sent to outstanding signers. Example: 'True'.
            name (string): Name of the signature request. Example: 'name'.
            prefill_tags (array): When a document contains sign-related tags in the content, you can prefill them using this `prefill_tags` by referencing the 'id' of the tag as the `external_id` field of the prefill tag.
            days_valid (integer): Set the number of days after which the created signature request will automatically expire if not completed. By default, we do not apply any expiration date on signature requests, and the signature request does not expire. Example: '2'.
            external_id (string): This can be used to reference an ID in an external system that the sign request is related to. Example: '123'.
            template_id (string): When a signature request is created from a template this field will indicate the id of that template. Example: '123075213-af2c8822-3ef2-4952-8557-52d69c2fe9cb'.
            external_system_name (string): Used as an optional system name to appear in the signature log next to the signers who have been assigned the `embed_url_external_id`. Example: 'Box'.
            source_files (array): List of files to create a signing document from. This is currently limited to ten files. Only the ID and type fields are required for each file.
            signature_color (string): Force a specific color for the signature (blue, black, or red) Example: 'blue'.
            signers (array): Array of signers for the signature request. 35 is the
        max number of signers permitted.

        **Note**: It may happen that some signers belong to conflicting [segments](r://shield-information-barrier-segment-member) (user groups).
        This means that due to the security policies, users are assigned to segments to prevent exchanges or communication that could lead to ethical conflicts.
        In such a case, an attempt to send the sign request will result in an error.

        Read more about [segments and ethical walls](https://support.box.com/hc/en-us/articles/9920431507603-Understanding-Information-Barriers#h_01GFVJEHQA06N7XEZ4GCZ9GFAQ).
            parent_folder (string): parent_folder

        Returns:
            dict[str, Any]: Returns a Box Sign request object.

        Tags:
            Box Sign requests
        """
        request_body = {
            'is_document_preparation_needed': is_document_preparation_needed,
            'redirect_url': redirect_url,
            'declined_redirect_url': declined_redirect_url,
            'are_text_signatures_enabled': are_text_signatures_enabled,
            'email_subject': email_subject,
            'email_message': email_message,
            'are_reminders_enabled': are_reminders_enabled,
            'name': name,
            'prefill_tags': prefill_tags,
            'days_valid': days_valid,
            'external_id': external_id,
            'template_id': template_id,
            'external_system_name': external_system_name,
            'source_files': source_files,
            'signature_color': signature_color,
            'signers': signers,
            'parent_folder': parent_folder,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/sign_requests"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_workflows(self, folder_id, trigger_type=None, limit=None, marker=None) -> dict[str, Any]:
        """
        Retrieves a list of workflows filtered by folder ID, trigger type, and pagination controls (limit and marker) using the GET method at the "/workflows" endpoint.

        Args:
            folder_id (string): The unique identifier that represent a folder. The ID for any folder can be determined
        by visiting this folder in the web application
        and copying the ID from the URL. For example,
        for the URL `
        the `folder_id` is `123`. The root folder of a Box account is
        always represented by the ID `0`. Example: '12345'.
            trigger_type (string): Type of trigger to search for. Example: 'WORKFLOW_MANUAL_START'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.

        Returns:
            dict[str, Any]: Returns the workflow.

        Tags:
            Workflows
        """
        url = f"{self.base_url}/workflows"
        query_params = {k: v for k, v in [('folder_id', folder_id), ('trigger_type', trigger_type), ('limit', limit), ('marker', marker)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_workflows_id_start(self, workflow_id, type=None, flow=None, files=None, folder=None, outcomes=None) -> Any:
        """
        Starts the specified workflow identified by workflow_id via a POST request, triggering its execution without returning content.

        Args:
            workflow_id (string): workflow_id
            type (string): The type of the parameters object Example: 'workflow_parameters'.
            flow (object): The flow that will be triggered
            files (array): The array of files for which the workflow should start. All files
        must be in the workflow's configured folder.
            folder (object): The folder object for which the workflow is configured.
            outcomes (array): A configurable outcome the workflow should complete.

        Returns:
            Any: Starts the workflow.

        Tags:
            Workflows
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        request_body = {
            'type': type,
            'flow': flow,
            'files': files,
            'folder': folder,
            'outcomes': outcomes,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/workflows/{workflow_id}/start"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sign_templates(self, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a list of sign templates, allowing pagination through the use of a marker and a limit parameter to control the number of results returned.

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: Returns a collection of templates.

        Tags:
            Box Sign templates
        """
        url = f"{self.base_url}/sign_templates"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sign_templates_id(self, template_id) -> dict[str, Any]:
        """
        Retrieves details of a specific sign template identified by the provided `template_id` using the GET method.

        Args:
            template_id (string): template_id

        Returns:
            dict[str, Any]: Returns details of a template.

        Tags:
            Box Sign templates
        """
        if template_id is None:
            raise ValueError("Missing required parameter 'template_id'")
        url = f"{self.base_url}/sign_templates/{template_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_integration_mappings_slack(self, marker=None, limit=None, partner_item_type=None, partner_item_id=None, box_item_id=None, box_item_type=None, is_manually_created=None) -> dict[str, Any]:
        """
        Retrieves a list of Slack integration mappings with optional filtering by marker, limit, partner and Box item types and IDs, and manual creation status.

        Args:
            marker (string): Defines the position marker at which to begin returning results. This is
        used when paginating using marker-based pagination. This requires `usemarker` to be set to `true`. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.
            partner_item_type (string): Mapped item type, for which the mapping should be returned Example: 'channel'.
            partner_item_id (string): ID of the mapped item, for which the mapping should be returned Example: '12345'.
            box_item_id (string): Box item ID, for which the mappings should be returned Example: '12345'.
            box_item_type (string): Box item type, for which the mappings should be returned Example: 'folder'.
            is_manually_created (boolean): Whether the mapping has been manually created Example: 'True'.

        Returns:
            dict[str, Any]: Returns a collection of integration mappings

        Tags:
            Integration mappings
        """
        url = f"{self.base_url}/integration_mappings/slack"
        query_params = {k: v for k, v in [('marker', marker), ('limit', limit), ('partner_item_type', partner_item_type), ('partner_item_id', partner_item_id), ('box_item_id', box_item_id), ('box_item_type', box_item_type), ('is_manually_created', is_manually_created)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_integration_mappings_slack(self, partner_item=None, box_item=None, options=None) -> dict[str, Any]:
        """
        Creates a Slack integration mapping by associating a Slack channel with a Box item using the POST method.

        Args:
            partner_item (string): partner_item
            box_item (string): box_item
            options (string): options

        Returns:
            dict[str, Any]: Returns the created integration mapping.

        Tags:
            Integration mappings
        """
        request_body = {
            'partner_item': partner_item,
            'box_item': box_item,
            'options': options,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/integration_mappings/slack"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_integration_mappings_slack_id(self, integration_mapping_id, box_item=None, options=None) -> dict[str, Any]:
        """
        Updates an existing Slack integration mapping by modifying the mapping identified by the specified `integration_mapping_id`.

        Args:
            integration_mapping_id (string): integration_mapping_id
            box_item (string): box_item
            options (string): options

        Returns:
            dict[str, Any]: Returns the updated integration mapping object.

        Tags:
            Integration mappings
        """
        if integration_mapping_id is None:
            raise ValueError("Missing required parameter 'integration_mapping_id'")
        request_body = {
            'box_item': box_item,
            'options': options,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/integration_mappings/slack/{integration_mapping_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_integration_mappings_slack_id(self, integration_mapping_id) -> Any:
        """
        Deletes the Slack integration mapping identified by the integration_mapping_id, removing the link between the Slack channel and the Box folder without deleting either the folder or the channel.

        Args:
            integration_mapping_id (string): integration_mapping_id

        Returns:
            Any: Empty body in response

        Tags:
            Integration mappings
        """
        if integration_mapping_id is None:
            raise ValueError("Missing required parameter 'integration_mapping_id'")
        url = f"{self.base_url}/integration_mappings/slack/{integration_mapping_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_integration_mappings_teams(self, partner_item_type=None, partner_item_id=None, box_item_id=None, box_item_type=None) -> dict[str, Any]:
        """
        Retrieves a list of Teams integration mappings in an enterprise, allowing filtering by partner item type, partner item ID, Box item ID, and Box item type.

        Args:
            partner_item_type (string): Mapped item type, for which the mapping should be returned Example: 'channel'.
            partner_item_id (string): ID of the mapped item, for which the mapping should be returned Example: '12345'.
            box_item_id (string): Box item ID, for which the mappings should be returned Example: '12345'.
            box_item_type (string): Box item type, for which the mappings should be returned Example: 'folder'.

        Returns:
            dict[str, Any]: Returns a collection of integration mappings

        Tags:
            Integration mappings
        """
        url = f"{self.base_url}/integration_mappings/teams"
        query_params = {k: v for k, v in [('partner_item_type', partner_item_type), ('partner_item_id', partner_item_id), ('box_item_id', box_item_id), ('box_item_type', box_item_type)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_integration_mappings_teams(self, partner_item=None, box_item=None) -> dict[str, Any]:
        """
        Creates a Microsoft Teams integration mapping by linking a Teams channel to a Box item using the Box API.

        Args:
            partner_item (string): partner_item
            box_item (string): box_item

        Returns:
            dict[str, Any]: Returns the created integration mapping.

        Tags:
            Integration mappings
        """
        request_body = {
            'partner_item': partner_item,
            'box_item': box_item,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/integration_mappings/teams"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_integration_mappings_teams_id(self, integration_mapping_id, box_item=None) -> dict[str, Any]:
        """
        Updates an existing Teams integration mapping identified by the provided `integration_mapping_id` using the Box API.

        Args:
            integration_mapping_id (string): integration_mapping_id
            box_item (string): box_item

        Returns:
            dict[str, Any]: Returns the updated integration mapping object.

        Tags:
            Integration mappings
        """
        if integration_mapping_id is None:
            raise ValueError("Missing required parameter 'integration_mapping_id'")
        request_body = {
            'box_item': box_item,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/integration_mappings/teams/{integration_mapping_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_integration_mappings_teams_id(self, integration_mapping_id) -> Any:
        """
        Deletes a Teams integration mapping identified by the integration_mapping_id, removing the link between a Teams channel and a Box folder without deleting either resource.

        Args:
            integration_mapping_id (string): integration_mapping_id

        Returns:
            Any: Empty body in response

        Tags:
            Integration mappings
        """
        if integration_mapping_id is None:
            raise ValueError("Missing required parameter 'integration_mapping_id'")
        url = f"{self.base_url}/integration_mappings/teams/{integration_mapping_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_ai_ask(self, mode=None, prompt=None, items=None, dialogue_history=None, include_citations=None, ai_agent=None) -> dict[str, Any]:
        """
        Processes AI-based questions submitted via POST requests to provide relevant answers or responses.

        Args:
            mode (string): Box AI handles text documents with text representations up to 1MB in size, or a maximum of 25 files, whichever comes first. If the text file size exceeds 1MB, the first 1MB of text representation will be processed. Box AI handles image documents with a resolution of 1024 x 1024 pixels, with a maximum of 5 images or 5 pages for multi-page images. If the number of image or image pages exceeds 5, the first 5 images or pages will be processed. If you set mode parameter to `single_item_qa`, the items array can have one element only. Currently Box AI does not support multi-modal requests. If both images and text are sent Box AI will only process the text. Example: 'multiple_item_qa'.
            prompt (string): The prompt provided by the client to be answered by the LLM. The prompt's length is limited to 10000 characters. Example: 'What is the value provided by public APIs based on this document?'.
            items (array): The items to be processed by the LLM, often files.
            dialogue_history (array): The history of prompts and answers previously passed to the LLM. This provides additional context to the LLM in generating the response.
            include_citations (boolean): A flag to indicate whether citations should be returned. Example: 'True'.
            ai_agent (string): ai_agent

        Returns:
            dict[str, Any]: A successful response including the answer from the LLM.

        Tags:
            AI
        """
        request_body = {
            'mode': mode,
            'prompt': prompt,
            'items': items,
            'dialogue_history': dialogue_history,
            'include_citations': include_citations,
            'ai_agent': ai_agent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ai/ask"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_ai_text_gen(self, prompt=None, items=None, dialogue_history=None, ai_agent=None) -> dict[str, Any]:
        """
        Generates text based on a given prompt using a specified model, returning the generated text as a response.

        Args:
            prompt (string): The prompt provided by the client to be answered by the LLM. The prompt's length is limited to 10000 characters. Example: 'Write an email to a client about the importance of public APIs.'.
            items (array): The items to be processed by the LLM, often files.
        The array can include **exactly one** element.

        **Note**: Box AI handles documents with text representations up to 1MB in size.
        If the file size exceeds 1MB, the first 1MB of text representation will be processed.
            dialogue_history (array): The history of prompts and answers previously passed to the LLM. This parameter provides the additional context to the LLM when generating the response.
            ai_agent (string): ai_agent

        Returns:
            dict[str, Any]: A successful response including the answer from the LLM.

        Tags:
            AI
        """
        request_body = {
            'prompt': prompt,
            'items': items,
            'dialogue_history': dialogue_history,
            'ai_agent': ai_agent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ai/text_gen"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_ai_agent_default(self, mode, language=None, model=None) -> Any:
        """
        Retrieves the default configuration settings for AI services, allowing clients to obtain parameters such as mode, language, and model for use or customization.

        Args:
            mode (string): The mode to filter the agent config to return. Example: 'ask'.
            language (string): The ISO language code to return the agent config for.
        If the language is not supported the default agent config is returned. Example: 'ja'.
            model (string): The model to return the default agent config for. Example: 'azure__openai__gpt_4o_mini'.

        Returns:
            Any: A successful response including the default agent configuration.
        This response can be one of the following four objects:
        * AI agent for questions
        * AI agent for text generation
        * AI agent for freeform metadata extraction
        * AI agent for structured metadata extraction.
        The response depends on the agent configuration requested in this endpoint.

        Tags:
            AI
        """
        url = f"{self.base_url}/ai_agent_default"
        query_params = {k: v for k, v in [('mode', mode), ('language', language), ('model', model)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_ai_extract(self, prompt=None, items=None, ai_agent=None) -> dict[str, Any]:
        """
        Extracts relevant data from specified sources using AI-powered text extraction techniques, returning clean and structured information based on the provided parameters.

        Args:
            prompt (string): The prompt provided to a Large Language Model (LLM) in the request. The prompt can be up to 10000 characters long and it can be an XML or a JSON schema. Example: '\\"fields\\":[{\\"type\\":\\"string\\",\\"key\\":\\"name\\",\\"displayName\\":\\"Name\\",\\"description\\":\\"The customer name\\",\\"prompt\\":\\"Name is always the first word in the document\\"},{\\"type\\":\\"date\\",\\"key\\":\\"last_contacted_at\\",\\"displayName\\":\\"Last Contacted At\\",\\"description\\":\\"When this customer was last contacted at\\"}]'.
            items (array): The items that LLM will process. Currently, you can use files only.
            ai_agent (string): ai_agent

        Returns:
            dict[str, Any]: A response including the answer from the LLM.

        Tags:
            AI
        """
        request_body = {
            'prompt': prompt,
            'items': items,
            'ai_agent': ai_agent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ai/extract"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_ai_extract_structured(self, items=None, metadata_template=None, fields=None, ai_agent=None) -> dict[str, Any]:
        """
        Extracts structured data from unstructured sources using AI-powered techniques, returning formatted data in a predefined schema.

        Args:
            items (array): The items to be processed by the LLM. Currently you can use files only.
            metadata_template (object): The metadata template containing the fields to extract.
        For your request to work, you must provide either `metadata_template` or `fields`, but not both.
            fields (array): The fields to be extracted from the provided items.
        For your request to work, you must provide either `metadata_template` or `fields`, but not both.
            ai_agent (string): ai_agent

        Returns:
            dict[str, Any]: A successful response including the answer from the LLM.

        Tags:
            AI
        """
        request_body = {
            'items': items,
            'metadata_template': metadata_template,
            'fields': fields,
            'ai_agent': ai_agent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ai/extract_structured"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_ai_agents(self, mode=None, fields=None, agent_state=None, include_box_default=None, marker=None, limit=None) -> dict[str, Any]:
        """
        Retrieves a filtered and paginated list of AI agents with optional parameters to specify mode, fields, agent state, inclusion of default box settings, marker, and limit.

        Args:
            mode (array): The mode to filter the agent config to return. Possible values are: `ask`, `text_gen`, and `extract`. Example: "['ask', 'text_gen', 'extract']".
            fields (array): The fields to return in the response. Example: "['ask', 'text_gen', 'extract']".
            agent_state (array): The state of the agents to return. Possible values are: `enabled`, `disabled` and `enabled_for_selected_users`. Example: "['enabled']".
            include_box_default (boolean): Whether to include the Box default agents in the response. Example: 'True'.
            marker (string): Defines the position marker at which to begin returning results. Example: 'JV9IRGZmieiBasejOG9yDCRNgd2ymoZIbjsxbJMjIs3kioVii'.
            limit (integer): The maximum number of items to return per page. Example: '1000'.

        Returns:
            dict[str, Any]: A successful response including the agents list.

        Tags:
            AI Studio
        """
        url = f"{self.base_url}/ai_agents"
        query_params = {k: v for k, v in [('mode', mode), ('fields', fields), ('agent_state', agent_state), ('include_box_default', include_box_default), ('marker', marker), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_ai_agents(self, type=None, name=None, access_state=None, icon_reference=None, allowed_entities=None, ask=None, text_gen=None, extract=None) -> dict[str, Any]:
        """
        Creates an AI agent instance using the POST method at the "/ai_agents" endpoint, enabling integration of AI functionalities into applications.

        Args:
            type (string): The type of agent used to handle queries. Example: 'ai_agent'.
            name (string): The name of the AI Agent. Example: 'My AI Agent'.
            access_state (string): The state of the AI Agent. Possible values are: `enabled`, `disabled`, and `enabled_for_selected_users`. Example: 'enabled'.
            icon_reference (string): The icon reference of the AI Agent. It should have format of the URL `https://cdn01.boxcdn.net/app-assets/aistudio/avatars/<file_name>`
        where possible values of `file_name` are: `logo_boxAi.png`,`logo_stamp.png`,`logo_legal.png`,`logo_finance.png`,`logo_config.png`,`logo_handshake.png`,`logo_analytics.png`,`logo_classification.png` Example: 'https://cdn01.boxcdn.net/app-assets/aistudio/avatars/logo_analytics.svg'.
            allowed_entities (array): List of allowed users or groups.
            ask (object): The AI Agent to be used for ask.
            text_gen (object): The AI agent used for generating text.
            extract (object): The AI Agent to be used for extraction.

        Returns:
            dict[str, Any]: Definition of created AI agent.

        Tags:
            AI Studio
        """
        request_body = {
            'type': type,
            'name': name,
            'access_state': access_state,
            'icon_reference': icon_reference,
            'allowed_entities': allowed_entities,
            'ask': ask,
            'text_gen': text_gen,
            'extract': extract,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ai_agents"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_ai_agents_id(self, agent_id, type=None, name=None, access_state=None, icon_reference=None, allowed_entities=None, ask=None, text_gen=None, extract=None) -> dict[str, Any]:
        """
        Updates the configuration or details of an AI agent identified by agent_id using the PUT method.

        Args:
            agent_id (string): agent_id
            type (string): The type of agent used to handle queries. Example: 'ai_agent'.
            name (string): The name of the AI Agent. Example: 'My AI Agent'.
            access_state (string): The state of the AI Agent. Possible values are: `enabled`, `disabled`, and `enabled_for_selected_users`. Example: 'enabled'.
            icon_reference (string): The icon reference of the AI Agent. It should have format of the URL `https://cdn01.boxcdn.net/app-assets/aistudio/avatars/<file_name>`
        where possible values of `file_name` are: `logo_boxAi.png`,`logo_stamp.png`,`logo_legal.png`,`logo_finance.png`,`logo_config.png`,`logo_handshake.png`,`logo_analytics.png`,`logo_classification.png` Example: 'https://cdn01.boxcdn.net/app-assets/aistudio/avatars/logo_analytics.svg'.
            allowed_entities (array): List of allowed users or groups.
            ask (object): The AI Agent to be used for ask.
            text_gen (object): The AI agent used for generating text.
            extract (object): The AI Agent to be used for extraction.

        Returns:
            dict[str, Any]: Definition of created AI agent.

        Tags:
            AI Studio
        """
        if agent_id is None:
            raise ValueError("Missing required parameter 'agent_id'")
        request_body = {
            'type': type,
            'name': name,
            'access_state': access_state,
            'icon_reference': icon_reference,
            'allowed_entities': allowed_entities,
            'ask': ask,
            'text_gen': text_gen,
            'extract': extract,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ai_agents/{agent_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_ai_agents_id(self, agent_id, fields=None) -> dict[str, Any]:
        """
        Retrieves information about a specific AI agent identified by its ID and optionally includes additional fields specified in the query parameters.

        Args:
            agent_id (string): agent_id
            fields (array): The fields to return in the response. Example: "['ask', 'text_gen', 'extract']".

        Returns:
            dict[str, Any]: A successful response including the agent.

        Tags:
            AI Studio
        """
        if agent_id is None:
            raise ValueError("Missing required parameter 'agent_id'")
        url = f"{self.base_url}/ai_agents/{agent_id}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_ai_agents_id(self, agent_id) -> Any:
        """
        Deletes an AI agent identified by the provided agent ID using the DELETE method and returns a status indicating the outcome of the operation.

        Args:
            agent_id (string): agent_id

        Returns:
            Any: A successful response with no content.

        Tags:
            AI Studio
        """
        if agent_id is None:
            raise ValueError("Missing required parameter 'agent_id'")
        url = f"{self.base_url}/ai_agents/{agent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.get_authorize,
            self.get_files_id,
            self.post_files_id,
            self.put_files_id,
            self.delete_files_id,
            self.get_files_id_app_item_associations,
            self.get_files_id_content,
            self.options_files_content,
            self.post_files_upload_sessions,
            self.post_files_id_upload_sessions,
            self.get_files_upload_sessions_id,
            self.delete_files_upload_sessions_id,
            self.get_files_upload_sessions_id_parts,
            self.post_files_upload_sessions_id_commit,
            self.post_files_id_copy,
            self.get_files_id_thumbnail_id,
            self.get_files_id_collaborations,
            self.get_files_id_comments,
            self.get_files_id_tasks,
            self.get_files_id_trash,
            self.delete_files_id_trash,
            self.get_files_id_versions,
            self.get_files_id_versions_id,
            self.delete_files_id_versions_id,
            self.put_files_id_versions_id,
            self.post_files_id_versions_current,
            self.get_files_id_metadata,
            self.get_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo,
            self.post_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo,
            self.delete_files_id_metadata_enterprise_security_classification_6_vmvochw_uwo,
            self.get_files_id_metadata_id_id,
            self.delete_files_id_metadata_id_id,
            self.get_files_id_metadata_global_box_skills_cards,
            self.post_files_id_metadata_global_box_skills_cards,
            self.delete_files_id_metadata_global_box_skills_cards,
            self.get_files_id_watermark,
            self.put_files_id_watermark,
            self.delete_files_id_watermark,
            self.get_file_requests_id,
            self.put_file_requests_id,
            self.delete_file_requests_id,
            self.post_file_requests_id_copy,
            self.get_folders_id,
            self.post_folders_id,
            self.put_folders_id,
            self.delete_folders_id,
            self.get_folders_id_app_item_associations,
            self.get_folders_id_items,
            self.post_folders,
            self.post_folders_id_copy,
            self.get_folders_id_collaborations,
            self.get_folders_id_trash,
            self.delete_folders_id_trash,
            self.get_folders_id_metadata,
            self.get_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo,
            self.post_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo,
            self.delete_folders_id_metadata_enterprise_security_classification_6_vmvochw_uwo,
            self.get_folders_id_metadata_id_id,
            self.delete_folders_id_metadata_id_id,
            self.get_folders_trash_items,
            self.get_folders_id_watermark,
            self.put_folders_id_watermark,
            self.delete_folders_id_watermark,
            self.get_folder_locks,
            self.post_folder_locks,
            self.delete_folder_locks_id,
            self.get_metadata_templates,
            self.get_metadata_templates_enterprise_security_classification_6_vmvochw_uwo_schema,
            self.put_metadata_templates_enterprise_security_classification_6_vmvochw_uwo_schema_add,
            self.get_metadata_templates_id_id_schema,
            self.delete_metadata_templates_id_id_schema,
            self.get_metadata_templates_id,
            self.get_metadata_templates_global,
            self.get_metadata_templates_enterprise,
            self.post_metadata_templates_schema,
            self.post_metadata_templates_schema_classifications,
            self.get_metadata_cascade_policies,
            self.post_metadata_cascade_policies,
            self.get_metadata_cascade_policies_id,
            self.delete_metadata_cascade_policies_id,
            self.post_metadata_cascade_policies_id_apply,
            self.post_metadata_queries_execute_read,
            self.get_comments_id,
            self.put_comments_id,
            self.delete_comments_id,
            self.post_comments,
            self.get_collaborations_id,
            self.put_collaborations_id,
            self.delete_collaborations_id,
            self.get_collaborations,
            self.post_collaborations,
            self.get_search,
            self.post_tasks,
            self.get_tasks_id,
            self.put_tasks_id,
            self.delete_tasks_id,
            self.get_tasks_id_assignments,
            self.post_task_assignments,
            self.get_task_assignments_id,
            self.put_task_assignments_id,
            self.delete_task_assignments_id,
            self.get_shared_items,
            self.get_files_id_get_shared_link,
            self.put_files_id_add_shared_link,
            self.put_files_id_update_shared_link,
            self.put_files_id_remove_shared_link,
            self.get_shared_items_folders,
            self.get_folders_id_get_shared_link,
            self.put_folders_id_add_shared_link,
            self.put_folders_id_update_shared_link,
            self.put_folders_id_remove_shared_link,
            self.post_web_links,
            self.get_web_links_id,
            self.post_web_links_id,
            self.put_web_links_id,
            self.delete_web_links_id,
            self.get_web_links_id_trash,
            self.delete_web_links_id_trash,
            self.get_shared_items_web_links,
            self.get_web_links_id_get_shared_link,
            self.put_web_links_id_add_shared_link,
            self.put_web_links_id_update_shared_link,
            self.put_web_links_id_remove_shared_link,
            self.get_shared_items_app_items,
            self.get_users,
            self.post_users,
            self.get_users_me,
            self.post_users_terminate_sessions,
            self.get_users_id,
            self.put_users_id,
            self.delete_users_id,
            self.get_users_id_avatar,
            self.delete_users_id_avatar,
            self.put_users_id_folders_0,
            self.get_users_id_email_aliases,
            self.post_users_id_email_aliases,
            self.delete_users_id_email_aliases_id,
            self.get_users_id_memberships,
            self.post_invites,
            self.get_invites_id,
            self.get_groups,
            self.post_groups,
            self.post_groups_terminate_sessions,
            self.get_groups_id,
            self.put_groups_id,
            self.delete_groups_id,
            self.get_groups_id_memberships,
            self.get_groups_id_collaborations,
            self.post_group_memberships,
            self.get_group_memberships_id,
            self.put_group_memberships_id,
            self.delete_group_memberships_id,
            self.get_webhooks,
            self.post_webhooks,
            self.get_webhooks_id,
            self.put_webhooks_id,
            self.delete_webhooks_id,
            self.put_skill_invocations_id,
            self.options_events,
            self.get_events,
            self.get_collections,
            self.get_collections_id_items,
            self.get_collections_id,
            self.get_recent_items,
            self.get_retention_policies,
            self.post_retention_policies,
            self.get_retention_policies_id,
            self.put_retention_policies_id,
            self.delete_retention_policies_id,
            self.get_retention_policies_id_assignments,
            self.post_retention_policy_assignments,
            self.get_retention_policy_assignments_id,
            self.delete_retention_policy_assignments_id,
            self.get_retention_policy_assignments_id_files_under_retention,
            self.get_retention_policy_assignments_id_file_versions_under_retention,
            self.get_legal_hold_policies,
            self.post_legal_hold_policies,
            self.get_legal_hold_policies_id,
            self.put_legal_hold_policies_id,
            self.delete_legal_hold_policies_id,
            self.get_legal_hold_policy_assignments,
            self.post_legal_hold_policy_assignments,
            self.get_legal_hold_policy_assignments_id,
            self.delete_legal_hold_policy_assignments_id,
            self.get_legal_hold_policy_assignments_id_files_on_hold,
            self.get_file_version_retentions,
            self.get_legal_hold_policy_assignments_id_file_versions_on_hold,
            self.get_file_version_retentions_id,
            self.get_file_version_legal_holds_id,
            self.get_file_version_legal_holds,
            self.get_shield_information_barriers_id,
            self.post_shield_information_barriers_change_status,
            self.get_shield_information_barriers,
            self.post_shield_information_barriers,
            self.get_shield_information_barrier_reports,
            self.post_shield_information_barrier_reports,
            self.get_shield_information_barrier_reports_id,
            self.get_shield_information_barrier_segments_id,
            self.delete_shield_information_barrier_segments_id,
            self.put_shield_information_barrier_segments_id,
            self.get_shield_information_barrier_segments,
            self.post_shield_information_barrier_segments,
            self.get_shield_information_barrier_segment_members_id,
            self.delete_shield_information_barrier_segment_members_id,
            self.get_shield_information_barrier_segment_members,
            self.post_shield_information_barrier_segment_members,
            self.get_shield_information_barrier_segment_restrictions_id,
            self.delete_shield_information_barrier_segment_restrictions_id,
            self.get_shield_information_barrier_segment_restrictions,
            self.post_shield_information_barrier_segment_restrictions,
            self.get_device_pinners_id,
            self.delete_device_pinners_id,
            self.get_enterprises_id_device_pinners,
            self.get_terms_of_services,
            self.post_terms_of_services,
            self.get_terms_of_services_id,
            self.put_terms_of_services_id,
            self.get_terms_of_service_user_statuses,
            self.post_terms_of_service_user_statuses,
            self.put_terms_of_service_user_statuses_id,
            self.get_collaboration_whitelist_entries,
            self.post_collaboration_whitelist_entries,
            self.get_collaboration_whitelist_entries_id,
            self.delete_collaboration_whitelist_entries_id,
            self.get_collaboration_whitelist_exempt_targets,
            self.post_collaboration_whitelist_exempt_targets,
            self.get_collaboration_whitelist_exempt_targets_id,
            self.delete_collaboration_whitelist_exempt_targets_id,
            self.get_storage_policies,
            self.get_storage_policies_id,
            self.get_storage_policy_assignments,
            self.post_storage_policy_assignments,
            self.get_storage_policy_assignments_id,
            self.put_storage_policy_assignments_id,
            self.delete_storage_policy_assignments_id,
            self.post_zip_downloads,
            self.get_zip_downloads_id_content,
            self.get_zip_downloads_id_status,
            self.post_sign_requests_id_cancel,
            self.post_sign_requests_id_resend,
            self.get_sign_requests_id,
            self.get_sign_requests,
            self.post_sign_requests,
            self.get_workflows,
            self.post_workflows_id_start,
            self.get_sign_templates,
            self.get_sign_templates_id,
            self.get_integration_mappings_slack,
            self.post_integration_mappings_slack,
            self.put_integration_mappings_slack_id,
            self.delete_integration_mappings_slack_id,
            self.get_integration_mappings_teams,
            self.post_integration_mappings_teams,
            self.put_integration_mappings_teams_id,
            self.delete_integration_mappings_teams_id,
            self.post_ai_ask,
            self.post_ai_text_gen,
            self.get_ai_agent_default,
            self.post_ai_extract,
            self.post_ai_extract_structured,
            self.get_ai_agents,
            self.post_ai_agents,
            self.put_ai_agents_id,
            self.get_ai_agents_id,
            self.delete_ai_agents_id
        ]
