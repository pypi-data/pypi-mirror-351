import typing

import grpc.aio
from grpc import RpcError
from grpc.aio import ClientCallDetails, Metadata

from union.remote._client.auth._authenticators.base import Authenticator


class _BaseAuthInterceptor:
    """
    Base class for all auth interceptors that provides common authentication functionality.
    """

    def __init__(self, get_authenticator: typing.Callable[[], Authenticator]):
        self._get_authenticator = get_authenticator
        self._authenticator = None

    @property
    def authenticator(self) -> Authenticator:
        if self._authenticator is None:
            self._authenticator = self._get_authenticator()
        return self._authenticator

    async def _call_details_with_auth_metadata(
        self, client_call_details: grpc.aio.ClientCallDetails
    ) -> (grpc.aio.ClientCallDetails, str):
        """
        Returns new ClientCallDetails with authentication metadata added.

        This method retrieves authentication metadata from the authenticator and adds it to the
        client call details. If no authentication metadata is available, the original client call
        details are returned unchanged.

        :param client_call_details: The original client call details containing method, timeout, metadata,
                                   credentials, and wait_for_ready settings
        :return: Updated client call details with authentication metadata added to the existing metadata
        """
        metadata = client_call_details.metadata
        auth_metadata = await self.authenticator.get_grpc_call_auth_metadata()
        if auth_metadata:
            metadata = client_call_details.metadata or Metadata()
            for k, v in auth_metadata.pairs.items():
                metadata.add(k, v)

        return client_call_details._replace(metadata=metadata), auth_metadata.creds_id if auth_metadata else None


class AuthUnaryUnaryInterceptor(_BaseAuthInterceptor, grpc.aio.UnaryUnaryClientInterceptor):
    """
    Interceptor for unary-unary RPC calls that adds authentication metadata.
    """

    async def intercept_unary_unary(
        self,
        continuation: typing.Callable,
        client_call_details: ClientCallDetails,
        request: typing.Any,
    ):
        """
        Intercepts unary-unary calls and adds auth metadata if available. On Unauthenticated, resets the token and
        refreshes and then retries with the new token.

        This method first adds authentication metadata to the client call details, then attempts to make the RPC call.
        If the call fails with an UNAUTHENTICATED or UNKNOWN status code, it refreshes the credentials and retries
        the call with the new authentication metadata.

        :param continuation: Function to continue the RPC call chain with the updated call details
        :param client_call_details: Details about the RPC call including method, timeout, metadata, credentials,
        and wait_for_ready
        :param request: The request message to be sent to the server
        :return: The response from the RPC call after successful authentication
        :raises: grpc.aio.AioRpcError if the call fails for reasons other than authentication
        """
        updated_call_details, creds_id = await self._call_details_with_auth_metadata(client_call_details)
        try:
            return await (await continuation(updated_call_details, request))
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED or e.code() == grpc.StatusCode.UNKNOWN:
                await self.authenticator.refresh_credentials(creds_id=creds_id)
                updated_call_details, _ = await self._call_details_with_auth_metadata(client_call_details)
                return await (await continuation(updated_call_details, request))
            raise e


class AuthUnaryStreamInterceptor(_BaseAuthInterceptor, grpc.aio.UnaryStreamClientInterceptor):
    """
    Interceptor for unary-stream RPC calls that adds authentication metadata.
    """

    async def intercept_unary_stream(
        self, continuation: typing.Callable, client_call_details: grpc.aio.ClientCallDetails, request: typing.Any
    ):
        """
        Intercepts unary-stream calls and adds auth metadata if available.

        This method first adds authentication metadata to the client call details, then attempts to make the RPC call.
        If the call fails with an UNAUTHENTICATED or UNKNOWN status code, it refreshes the credentials and retries
        the call with the new authentication metadata.

        :param continuation: Function to continue the RPC call chain with the updated call details
        :param client_call_details: Details about the RPC call including method, timeout, metadata, credentials,
        and wait_for_ready
        :param request: The request message to be sent to the server
        :return: A stream of responses from the RPC call after successful authentication
        :raises: grpc.aio.AioRpcError if the call fails for reasons other than authentication
        """
        call_details, creds_id = await self._call_details_with_auth_metadata(client_call_details)

        async def response_iterator() -> typing.AsyncIterator[typing.Any]:
            call = await continuation(call_details, request)
            try:
                async for response in call:
                    yield response
            except grpc.aio.AioRpcError as e:
                if e.code() == grpc.StatusCode.UNAUTHENTICATED or e.code() == grpc.StatusCode.UNKNOWN:
                    await self.authenticator.refresh_credentials(creds_id=creds_id)
                    updated_call_details, _ = await self._call_details_with_auth_metadata(client_call_details)
                    async for response in await continuation(updated_call_details, request):
                        yield response
                raise e

        return response_iterator()


class AuthStreamUnaryInterceptor(_BaseAuthInterceptor, grpc.aio.StreamUnaryClientInterceptor):
    """
    Interceptor for stream-unary RPC calls that adds authentication metadata.
    """

    async def intercept_stream_unary(
        self,
        continuation: typing.Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request_iterator: typing.Any,
    ):
        """
        Intercepts stream-unary calls and adds auth metadata if available.

        This method first adds authentication metadata to the client call details, then attempts to make the RPC call.
        If the call fails with an UNAUTHENTICATED or UNKNOWN status code, it refreshes the credentials and retries
        the call with the new authentication metadata.

        :param continuation: Function to continue the RPC call chain with the updated call details
        :param client_call_details: Details about the RPC call including method, timeout, metadata, credentials,
        and wait_for_ready
        :param request_iterator: An iterator of request messages to be sent to the server
        :return: The response from the RPC call after successful authentication
        :raises: grpc.aio.AioRpcError if the call fails for reasons other than authentication
        """
        updated_call_details, creds_id = await self._call_details_with_auth_metadata(client_call_details)
        try:
            call = await continuation(updated_call_details, request_iterator)
            return await call
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED or e.code() == grpc.StatusCode.UNKNOWN:
                await self.authenticator.refresh_credentials(creds_id=creds_id)
                updated_call_details, _ = await self._call_details_with_auth_metadata(client_call_details)
                call = await continuation(updated_call_details, request_iterator)
                return await call
            raise e


class AuthStreamStreamInterceptor(_BaseAuthInterceptor, grpc.aio.StreamStreamClientInterceptor):
    """
    Interceptor for stream-stream RPC calls that adds authentication metadata.
    """

    async def intercept_stream_stream(
        self,
        continuation: typing.Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request_iterator: typing.Any,
    ):
        """
        Intercepts stream-stream calls and adds auth metadata if available.

        This method first adds authentication metadata to the client call details, then attempts to make the RPC call.
        If the call fails with an UNAUTHENTICATED or UNKNOWN status code, it refreshes the credentials and retries
        the call with the new authentication metadata.

        :param continuation: Function to continue the RPC call chain with the updated call details
        :param client_call_details: Details about the RPC call including method, timeout, metadata, credentials,
        and wait_for_ready
        :param request_iterator: An iterator of request messages to be sent to the server
        :return: A stream of responses from the RPC call after successful authentication
        :raises: grpc.aio.AioRpcError if the call fails for reasons other than authentication
        """
        updated_call_details, creds_id = await self._call_details_with_auth_metadata(client_call_details)
        try:
            fut = await (await continuation(updated_call_details, request_iterator))
            return fut
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED or e.code() == grpc.StatusCode.UNKNOWN:
                await self.authenticator.refresh_credentials(creds_id=creds_id)
                updated_call_details, _ = await self._call_details_with_auth_metadata(client_call_details)
                return await (await continuation(updated_call_details, request_iterator))
            raise e
        except RpcError as e:
            raise e


# For backward compatibility, maintain the original class name but as a type alias
AuthUnaryInterceptor = AuthUnaryUnaryInterceptor
