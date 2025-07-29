from typing import Annotated, Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class TrelloApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        # Assuming {{baseURL}} represents the root like https://api.trello.com/1/
        # The specific resource paths (boards, cards) are added in each method based on the schema's server definitions
        super().__init__(name='trello', integration=integration, **kwargs)
        self.base_url = "{{baseURL}}"


    def get1_boards_id(self, key: Annotated[Any, ''] = None, token: Annotated[Any, ''] = None) -> Any:
        """
        Retrieve board details by ID from the API endpoint.

        Args:
            key: API authentication key or identifier (optional)
            token: Authentication token for API access (optional)

        Returns:
            Dictionary containing board details as returned by the API

        Raises:
            requests.exceptions.HTTPError: Raised for failed API responses (4XX/5XX status codes)

        Tags:
            board, get, api, management, important
        """
        # Schema server: {{baseURL}}boards, Schema path: /rAIRIVAI
        path = "boards/rAIRIVAI"
        url = f"{self.base_url}{path}"
        query_params = {
                "key": key,
                "token": token,
            }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get1_boards_id_lists(self, key: Annotated[Any, ''] = None, token: Annotated[Any, ''] = None) -> Any:
        """
        Retrieves lists for a specific board from the Trello API using its ID.

        Args:
            key: API key for Trello authentication.
            token: Authentication token for Trello API access.

        Returns:
            Parsed JSON response containing the board lists data from the Trello API.

        Raises:
            requests.HTTPError: Raised if the API request fails (non-2xx status code).

        Tags:
            board, lists, get, api, trello
        """
        # Schema server: {{baseURL}}boards, Schema path: /rAIRIVAI/lists
        path = "boards/rAIRIVAI/lists"
        url = f"{self.base_url}{path}"
        query_params = {
                "key": key,
                "token": token,
            }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post1_cards(self, desc: Annotated[Any, ''] = None, idBoard: Annotated[Any, ''] = None, idList: Annotated[Any, ''] = None, key: Annotated[Any, ''] = None, name: Annotated[Any, ''] = None, token: Annotated[Any, ''] = None) -> Any:
        """
        Creates a new card by sending a POST request to the /1/cards endpoint.

        Args:
            desc: Optional description of the card.
            idBoard: Optional identifier of the board where the card will be created.
            idList: Optional identifier of the list where the card will be created.
            key: Optional API key used for authentication.
            name: Optional name of the card.
            token: Optional token used for authentication.

        Returns:
            JSON response from the server upon successful creation of the card.

        Raises:
            requests.exceptions.HTTPError: Raised if the HTTP request encounters any issues, such as invalid status codes.

        Tags:
            create, card, management
        """
        request_body = {
            "desc": desc,
            "idBoard": idBoard,
            "idList": idList,
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        # Schema server: {{baseURL}}cards, Schema path: /
        path = "cards/"
        url = f"{self.base_url}{path}"
        query_params = {
                "key": key,
                "token": token,
            }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        # Use json=request_body for sending JSON body
        response = self._post(url, json=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get1_cards_id(self, key: Annotated[Any, ''] = None, token: Annotated[Any, ''] = None) -> Any:
        """
        Retrieve card details by ID using the API endpoint.

        Args:
            key: API key for authentication. If not provided, it is omitted from the request.
            token: Authentication token. If not provided, it is omitted from the request.

        Returns:
            JSON-formatted response containing card details.

        Raises:
            HTTPError: Raised if the API request fails with a non-2xx status code (e.g., 404 for invalid ID or 401 for invalid credentials).

        Tags:
            cards, get, api, authentication
        """
        # Schema server: {{baseURL}}cards, Schema path: /64513f05ce82b6b80d0cf85e
        path = "cards/64513f05ce82b6b80d0cf85e"
        url = f"{self.base_url}{path}"
        query_params = {
                "key": key,
                "token": token,
            }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put1_cards_id(self, desc: Annotated[Any, ''] = None, key: Annotated[Any, ''] = None, name: Annotated[Any, ''] = None, token: Annotated[Any, ''] = None) -> Any:
        """
        Updates a card by making a PUT request to the /1/cards/{id} endpoint with optional description, name, key, and token parameters.

        Args:
            desc: Optional description to update.
            key: Optional key parameter.
            name: Optional name to update.
            token: Optional token parameter.

        Returns:
            JSON response from the server.

        Raises:
            requests.HTTPError: If the server returns a status code that indicates an HTTP error.

        Tags:
            update, cards, management
        """
        request_body = {
            "desc": desc,
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        # Schema server: {{baseURL}}cards, Schema path: /64513f05ce82b6b80d0cf85e
        path = "cards/64513f05ce82b6b80d0cf85e"
        url = f"{self.base_url}{path}"
        query_params = {
                "key": key,
                "token": token,
            }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        # Use json=request_body for sending JSON body
        response = self._put(url, json=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete1_cards_id(self, key: Annotated[Any, ''] = None, token: Annotated[Any, ''] = None) -> Any:
        """
        Deletes a card with the specified ID by sending a DELETE request including key and token parameters.

        Args:
            key: OAuth key for authentication (exact purpose unclear from context)
            token: Access token for authorization (exact purpose unclear from context)

        Returns:
            Parsed JSON response from the DELETE request containing operation results

        Raises:
            HTTPError: If the HTTP request fails (4xx/5xx status codes)

        Tags:
            cards, delete
        """
        # Schema server: {{baseURL}}cards, Schema path: /64513b087161f7d443491538
        path = "cards/64513b087161f7d443491538"
        url = f"{self.base_url}{path}"
        query_params = {
                "key": key,
                "token": token,
            }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()


    def list_tools(self):
        return [

            self.get1_boards_id,
            self.get1_boards_id_lists,
            self.post1_cards,
            self.get1_cards_id,
            self.put1_cards_id,
            self.delete1_cards_id
        ]
