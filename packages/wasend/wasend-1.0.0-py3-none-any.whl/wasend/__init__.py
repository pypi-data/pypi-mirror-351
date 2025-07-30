r'''
# Wasend SDK

A powerful SDK for managing WhatsApp sessions across multiple programming languages. This SDK provides a simple and intuitive interface for creating, managing, and interacting with WhatsApp sessions.

## Features

* Create and manage WhatsApp sessions
* QR code authentication
* Session status management (start, stop, restart)
* Account protection features
* Message logging
* Webhook support
* Multi-language support (TypeScript/JavaScript, Python, Java, .NET, Go)

## Installation

### TypeScript/JavaScript (npm)

```bash
npm install @wasend/core
# or
yarn add @wasend/core
```

### Python (pip)

```bash
pip install wasend-dev
```

### Java (Maven)

```xml
<dependency>
    <groupId>com.wasend</groupId>
    <artifactId>wasend-core</artifactId>
    <version>1.0.0</version>
</dependency>
```

### .NET (NuGet)

```bash
dotnet add package Wasend.Core
```

### Go

```bash
go get github.com/wasenddev/wasend-sdk-go
```

## Quick Start

### TypeScript/JavaScript Example

```python
import { WasendClient } from '@wasend/core';

// Initialize the client
const client = new WasendClient({
    apiKey: 'your-api-key',
    baseUrl: 'https://api.wasend.dev'
});

// Create a new session
const session = await client.sessions.createSession({
    sessionName: 'my-whatsapp-session',
    phoneNumber: '+919876543210', // Example phone number
    enableAccountProtection: true,
    enableMessageLogging: true,
    enableWebhook: false
});

// Get QR code for authentication
const qrCode = await client.sessions.getQRCode(session.uniqueSessionId);
console.log('Scan this QR code with WhatsApp:', qrCode.data);

// Start the session
await client.sessions.startSession(session.uniqueSessionId);

// Get session information
const sessionInfo = await client.sessions.getSessionInfo(session.uniqueSessionId);
console.log('Session status:', sessionInfo.status);
```

## Session Management

### Creating a Session

```python
const session = await client.sessions.createSession({
    sessionName: 'my-whatsapp-session',
    phoneNumber: '+919876543210',
    enableAccountProtection: true,
    enableMessageLogging: true,
    enableWebhook: true,
    webhookUrl: 'https://your-webhook-url.com/callback'
});
```

### Session Configuration Options

* `sessionName`: A unique name for your session
* `phoneNumber`: The WhatsApp phone number to use (format: +[country code][number])
* `enableAccountProtection`: Enable additional security features
* `enableMessageLogging`: Enable message history logging
* `enableWebhook`: Enable webhook notifications
* `webhookUrl`: URL for receiving webhook notifications (required if enableWebhook is true)

### Managing Sessions

```python
// Get all sessions
const allSessions = await client.sessions.getAllSessions();

// Get specific session info
const sessionInfo = await client.sessions.getSessionInfo(sessionId);

// Start a session
await client.sessions.startSession(sessionId);

// Stop a session
await client.sessions.stopSession(sessionId);

// Restart a session
await client.sessions.restartSession(sessionId);

// Delete a session
await client.sessions.deleteSession(sessionId);
```

## Authentication

### QR Code Authentication

1. Create a session
2. Get the QR code
3. Scan the QR code with WhatsApp on your phone
4. The session will automatically connect once scanned

```python
const qrCode = await client.sessions.getQRCode(sessionId);
console.log('QR Code data:', qrCode.data);
```

## Session Status

A session can have the following statuses:

* `CREATED`: Session has been created but not started
* `STARTING`: Session is in the process of starting
* `CONNECTED`: Session is connected and ready to use
* `STOPPED`: Session has been stopped
* `ERROR`: Session encountered an error

## Webhook Integration

To receive notifications about session events:

1. Enable webhooks when creating a session
2. Provide a valid webhook URL
3. Handle incoming webhook notifications on your server

```python
const session = await client.sessions.createSession({
    sessionName: 'webhook-enabled-session',
    phoneNumber: '+919876543210',
    enableWebhook: true,
    webhookUrl: 'https://your-server.com/webhook'
});
```

## Error Handling

```python
try {
    const session = await client.sessions.createSession({
        sessionName: 'test-session',
        phoneNumber: '+919876543210'
    });
} catch (error) {
    console.error('Error creating session:', error);
}
```

## Best Practices

1. Always store the `sessionId` after creating a session
2. Implement proper error handling
3. Use environment variables for API keys
4. Enable account protection for production sessions
5. Implement webhook handling for real-time updates
6. Regularly check session status
7. Clean up unused sessions

## Support

For support, please contact:

* Email: admin@wasend.dev
* Website: https://wasend.dev
* Documentation: https://docs.wasend.dev

## License

This SDK is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *


@jsii.data_type(
    jsii_type="@wasend/core.AccountInfo",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "name": "name", "plan": "plan"},
)
class AccountInfo:
    def __init__(
        self,
        *,
        id: builtins.str,
        name: builtins.str,
        plan: builtins.str,
    ) -> None:
        '''Account information structure.

        :param id: Account ID.
        :param name: Account name.
        :param plan: Account plan.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8d187f8daf4945ee8cc7af4c965fbd16ceba9a4a4f1a826ace5438a45da1cd0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument plan", value=plan, expected_type=type_hints["plan"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "name": name,
            "plan": plan,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Account ID.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Account name.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Account plan.'''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.ApiResponse",
    jsii_struct_bases=[],
    name_mapping={"success": "success", "data": "data", "error": "error"},
)
class ApiResponse:
    def __init__(
        self,
        *,
        success: builtins.bool,
        data: typing.Any = None,
        error: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Response from API calls.

        :param success: Whether the request was successful.
        :param data: The response data (if successful).
        :param error: Error message if the request failed.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f5feba71406aa1ad99458c7cdc2a9f785cd020e1fbbd5a6830e52fd8bb2382)
            check_type(argname="argument success", value=success, expected_type=type_hints["success"])
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
            check_type(argname="argument error", value=error, expected_type=type_hints["error"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "success": success,
        }
        if data is not None:
            self._values["data"] = data
        if error is not None:
            self._values["error"] = error

    @builtins.property
    def success(self) -> builtins.bool:
        '''Whether the request was successful.'''
        result = self._values.get("success")
        assert result is not None, "Required property 'success' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def data(self) -> typing.Any:
        '''The response data (if successful).'''
        result = self._values.get("data")
        return typing.cast(typing.Any, result)

    @builtins.property
    def error(self) -> typing.Optional[builtins.str]:
        '''Error message if the request failed.'''
        result = self._values.get("error")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.DownstreamInfo",
    jsii_struct_bases=[],
    name_mapping={
        "config": "config",
        "engine": "engine",
        "name": "name",
        "status": "status",
    },
)
class DownstreamInfo:
    def __init__(
        self,
        *,
        config: typing.Union["SessionConfig", typing.Dict[builtins.str, typing.Any]],
        engine: typing.Union["EngineStatus", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        status: builtins.str,
    ) -> None:
        '''Downstream connection information.

        :param config: Configuration for the downstream connection.
        :param engine: Engine status information.
        :param name: Name of the downstream connection.
        :param status: Status of the downstream connection.
        '''
        if isinstance(config, dict):
            config = SessionConfig(**config)
        if isinstance(engine, dict):
            engine = EngineStatus(**engine)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e85038298b8fa1b5985855072c2560ca953a48eea4a7ee8b9f750e8bc6f62348)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "config": config,
            "engine": engine,
            "name": name,
            "status": status,
        }

    @builtins.property
    def config(self) -> "SessionConfig":
        '''Configuration for the downstream connection.'''
        result = self._values.get("config")
        assert result is not None, "Required property 'config' is missing"
        return typing.cast("SessionConfig", result)

    @builtins.property
    def engine(self) -> "EngineStatus":
        '''Engine status information.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast("EngineStatus", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the downstream connection.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status(self) -> builtins.str:
        '''Status of the downstream connection.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DownstreamInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.EngineStatus",
    jsii_struct_bases=[],
    name_mapping={"gows": "gows", "grpc": "grpc"},
)
class EngineStatus:
    def __init__(
        self,
        *,
        gows: typing.Union["GowsStatus", typing.Dict[builtins.str, typing.Any]],
        grpc: typing.Union["GrpcStatus", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''Engine status information.

        :param gows: GoWS status.
        :param grpc: gRPC status.
        '''
        if isinstance(gows, dict):
            gows = GowsStatus(**gows)
        if isinstance(grpc, dict):
            grpc = GrpcStatus(**grpc)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62f98c4efad3df7d9dcd0fbf647c894254a448f6718f0c1fad58962182024475)
            check_type(argname="argument gows", value=gows, expected_type=type_hints["gows"])
            check_type(argname="argument grpc", value=grpc, expected_type=type_hints["grpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "gows": gows,
            "grpc": grpc,
        }

    @builtins.property
    def gows(self) -> "GowsStatus":
        '''GoWS status.'''
        result = self._values.get("gows")
        assert result is not None, "Required property 'gows' is missing"
        return typing.cast("GowsStatus", result)

    @builtins.property
    def grpc(self) -> "GrpcStatus":
        '''gRPC status.'''
        result = self._values.get("grpc")
        assert result is not None, "Required property 'grpc' is missing"
        return typing.cast("GrpcStatus", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EngineStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.GetAllSessionsResponse",
    jsii_struct_bases=[],
    name_mapping={"sessions": "sessions"},
)
class GetAllSessionsResponse:
    def __init__(
        self,
        *,
        sessions: typing.Sequence[typing.Union["SessionListItem", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''Response wrapper for getAllSessions.

        :param sessions: Array of sessions.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09647a94e3d8e4aee98f4628c3fa572a7d308b6f12281833bf5a01c156dec696)
            check_type(argname="argument sessions", value=sessions, expected_type=type_hints["sessions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "sessions": sessions,
        }

    @builtins.property
    def sessions(self) -> typing.List["SessionListItem"]:
        '''Array of sessions.'''
        result = self._values.get("sessions")
        assert result is not None, "Required property 'sessions' is missing"
        return typing.cast(typing.List["SessionListItem"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GetAllSessionsResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.GowsStatus",
    jsii_struct_bases=[],
    name_mapping={"connected": "connected", "found": "found"},
)
class GowsStatus:
    def __init__(self, *, connected: builtins.bool, found: builtins.bool) -> None:
        '''
        :param connected: 
        :param found: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9c788395f63b322df62cfa06c64f225e1401e968d5af857d8143e86d9b74616)
            check_type(argname="argument connected", value=connected, expected_type=type_hints["connected"])
            check_type(argname="argument found", value=found, expected_type=type_hints["found"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connected": connected,
            "found": found,
        }

    @builtins.property
    def connected(self) -> builtins.bool:
        result = self._values.get("connected")
        assert result is not None, "Required property 'connected' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def found(self) -> builtins.bool:
        result = self._values.get("found")
        assert result is not None, "Required property 'found' is missing"
        return typing.cast(builtins.bool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GowsStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.GrpcStatus",
    jsii_struct_bases=[],
    name_mapping={"client": "client", "stream": "stream"},
)
class GrpcStatus:
    def __init__(self, *, client: builtins.str, stream: builtins.str) -> None:
        '''
        :param client: 
        :param stream: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a90498c82c9829383ee4faed719fa2d55e4aaaa0a02c2c7519ed1097813a50e6)
            check_type(argname="argument client", value=client, expected_type=type_hints["client"])
            check_type(argname="argument stream", value=stream, expected_type=type_hints["stream"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client": client,
            "stream": stream,
        }

    @builtins.property
    def client(self) -> builtins.str:
        result = self._values.get("client")
        assert result is not None, "Required property 'client' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stream(self) -> builtins.str:
        result = self._values.get("stream")
        assert result is not None, "Required property 'stream' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GrpcStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.Message",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "id": "id",
        "sent_at": "sentAt",
        "status": "status",
        "to": "to",
    },
)
class Message:
    def __init__(
        self,
        *,
        content: builtins.str,
        id: builtins.str,
        sent_at: builtins.str,
        status: builtins.str,
        to: builtins.str,
    ) -> None:
        '''Message data structure.

        :param content: The content of the message.
        :param id: Unique identifier for the message.
        :param sent_at: Timestamp when the message was sent (ISO string).
        :param status: Message status.
        :param to: The recipient of the message.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e6ddabade18cb6b127a9542093b14870224ca085a4fedc56304aeee1c2f06ce)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument sent_at", value=sent_at, expected_type=type_hints["sent_at"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "id": id,
            "sent_at": sent_at,
            "status": status,
            "to": to,
        }

    @builtins.property
    def content(self) -> builtins.str:
        '''The content of the message.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''Unique identifier for the message.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sent_at(self) -> builtins.str:
        '''Timestamp when the message was sent (ISO string).'''
        result = self._values.get("sent_at")
        assert result is not None, "Required property 'sent_at' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status(self) -> builtins.str:
        '''Message status.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def to(self) -> builtins.str:
        '''The recipient of the message.'''
        result = self._values.get("to")
        assert result is not None, "Required property 'to' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Message(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.MessageRequest",
    jsii_struct_bases=[],
    name_mapping={"content": "content", "to": "to"},
)
class MessageRequest:
    def __init__(self, *, content: builtins.str, to: builtins.str) -> None:
        '''Message request structure.

        :param content: The content of the message.
        :param to: The recipient of the message.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa2d4015027c18549dff3d305605433dfdca504013c7fd0895520c8d64d08e82)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "to": to,
        }

    @builtins.property
    def content(self) -> builtins.str:
        '''The content of the message.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def to(self) -> builtins.str:
        '''The recipient of the message.'''
        result = self._values.get("to")
        assert result is not None, "Required property 'to' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MessageRequest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.NowebConfig",
    jsii_struct_bases=[],
    name_mapping={"mark_online": "markOnline", "store": "store"},
)
class NowebConfig:
    def __init__(
        self,
        *,
        mark_online: builtins.bool,
        store: typing.Union["NowebStoreConfig", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param mark_online: 
        :param store: 
        '''
        if isinstance(store, dict):
            store = NowebStoreConfig(**store)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1d9acc660dd7af1a46bcbe0beab4ac7f79e0cb52e2e591c905cb18a2e402a31)
            check_type(argname="argument mark_online", value=mark_online, expected_type=type_hints["mark_online"])
            check_type(argname="argument store", value=store, expected_type=type_hints["store"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mark_online": mark_online,
            "store": store,
        }

    @builtins.property
    def mark_online(self) -> builtins.bool:
        result = self._values.get("mark_online")
        assert result is not None, "Required property 'mark_online' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def store(self) -> "NowebStoreConfig":
        result = self._values.get("store")
        assert result is not None, "Required property 'store' is missing"
        return typing.cast("NowebStoreConfig", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NowebConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.NowebStoreConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "full_sync": "fullSync"},
)
class NowebStoreConfig:
    def __init__(self, *, enabled: builtins.bool, full_sync: builtins.bool) -> None:
        '''
        :param enabled: 
        :param full_sync: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3504aad6bb01adf6b4e052cec8a4b4630e3f6d4463e67757a39a236969ffb0c8)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument full_sync", value=full_sync, expected_type=type_hints["full_sync"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
            "full_sync": full_sync,
        }

    @builtins.property
    def enabled(self) -> builtins.bool:
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def full_sync(self) -> builtins.bool:
        result = self._values.get("full_sync")
        assert result is not None, "Required property 'full_sync' is missing"
        return typing.cast(builtins.bool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NowebStoreConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.QRCodeResponse",
    jsii_struct_bases=[],
    name_mapping={"data": "data"},
)
class QRCodeResponse:
    def __init__(self, *, data: builtins.str) -> None:
        '''QR code response.

        :param data: QR code data.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96354063aeb190a9953a739f8ddd730b166f0b989d0a398486425665f25137a3)
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data": data,
        }

    @builtins.property
    def data(self) -> builtins.str:
        '''QR code data.'''
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QRCodeResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.SessionConfig",
    jsii_struct_bases=[],
    name_mapping={
        "debug": "debug",
        "metadata": "metadata",
        "noweb": "noweb",
        "proxy": "proxy",
        "webhooks": "webhooks",
    },
)
class SessionConfig:
    def __init__(
        self,
        *,
        debug: builtins.bool,
        metadata: typing.Union["SessionMetadata", typing.Dict[builtins.str, typing.Any]],
        noweb: typing.Union[NowebConfig, typing.Dict[builtins.str, typing.Any]],
        proxy: typing.Any,
        webhooks: typing.Sequence[typing.Any],
    ) -> None:
        '''Session configuration.

        :param debug: Debug mode.
        :param metadata: User metadata.
        :param noweb: Noweb configuration.
        :param proxy: Proxy configuration.
        :param webhooks: Webhook configurations.
        '''
        if isinstance(metadata, dict):
            metadata = SessionMetadata(**metadata)
        if isinstance(noweb, dict):
            noweb = NowebConfig(**noweb)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4bda00ff00f4da8f5d020b9ae62f84aef28dfe5100c707bc597e0d613a8ca00)
            check_type(argname="argument debug", value=debug, expected_type=type_hints["debug"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument noweb", value=noweb, expected_type=type_hints["noweb"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument webhooks", value=webhooks, expected_type=type_hints["webhooks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "debug": debug,
            "metadata": metadata,
            "noweb": noweb,
            "proxy": proxy,
            "webhooks": webhooks,
        }

    @builtins.property
    def debug(self) -> builtins.bool:
        '''Debug mode.'''
        result = self._values.get("debug")
        assert result is not None, "Required property 'debug' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def metadata(self) -> "SessionMetadata":
        '''User metadata.'''
        result = self._values.get("metadata")
        assert result is not None, "Required property 'metadata' is missing"
        return typing.cast("SessionMetadata", result)

    @builtins.property
    def noweb(self) -> NowebConfig:
        '''Noweb configuration.'''
        result = self._values.get("noweb")
        assert result is not None, "Required property 'noweb' is missing"
        return typing.cast(NowebConfig, result)

    @builtins.property
    def proxy(self) -> typing.Any:
        '''Proxy configuration.'''
        result = self._values.get("proxy")
        assert result is not None, "Required property 'proxy' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def webhooks(self) -> typing.List[typing.Any]:
        '''Webhook configurations.'''
        result = self._values.get("webhooks")
        assert result is not None, "Required property 'webhooks' is missing"
        return typing.cast(typing.List[typing.Any], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SessionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.SessionCreateRequest",
    jsii_struct_bases=[],
    name_mapping={
        "phone_number": "phoneNumber",
        "session_name": "sessionName",
        "enable_account_protection": "enableAccountProtection",
        "enable_message_logging": "enableMessageLogging",
        "enable_webhook": "enableWebhook",
        "webhook_url": "webhookUrl",
    },
)
class SessionCreateRequest:
    def __init__(
        self,
        *,
        phone_number: builtins.str,
        session_name: builtins.str,
        enable_account_protection: typing.Optional[builtins.bool] = None,
        enable_message_logging: typing.Optional[builtins.bool] = None,
        enable_webhook: typing.Optional[builtins.bool] = None,
        webhook_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Session creation request body.

        :param phone_number: Phone number for the WhatsApp session.
        :param session_name: Name of the session.
        :param enable_account_protection: Enable account protection features. Default: false
        :param enable_message_logging: Enable message logging. Default: false
        :param enable_webhook: Enable webhook notifications. Default: false
        :param webhook_url: Webhook URL for notifications Required if enableWebhook is true.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e3cdcf8dd89941a7ff518341872e1a93509aae9d708132cd86835fcac559df4)
            check_type(argname="argument phone_number", value=phone_number, expected_type=type_hints["phone_number"])
            check_type(argname="argument session_name", value=session_name, expected_type=type_hints["session_name"])
            check_type(argname="argument enable_account_protection", value=enable_account_protection, expected_type=type_hints["enable_account_protection"])
            check_type(argname="argument enable_message_logging", value=enable_message_logging, expected_type=type_hints["enable_message_logging"])
            check_type(argname="argument enable_webhook", value=enable_webhook, expected_type=type_hints["enable_webhook"])
            check_type(argname="argument webhook_url", value=webhook_url, expected_type=type_hints["webhook_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "phone_number": phone_number,
            "session_name": session_name,
        }
        if enable_account_protection is not None:
            self._values["enable_account_protection"] = enable_account_protection
        if enable_message_logging is not None:
            self._values["enable_message_logging"] = enable_message_logging
        if enable_webhook is not None:
            self._values["enable_webhook"] = enable_webhook
        if webhook_url is not None:
            self._values["webhook_url"] = webhook_url

    @builtins.property
    def phone_number(self) -> builtins.str:
        '''Phone number for the WhatsApp session.'''
        result = self._values.get("phone_number")
        assert result is not None, "Required property 'phone_number' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def session_name(self) -> builtins.str:
        '''Name of the session.'''
        result = self._values.get("session_name")
        assert result is not None, "Required property 'session_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_account_protection(self) -> typing.Optional[builtins.bool]:
        '''Enable account protection features.

        :default: false
        '''
        result = self._values.get("enable_account_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_message_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable message logging.

        :default: false
        '''
        result = self._values.get("enable_message_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_webhook(self) -> typing.Optional[builtins.bool]:
        '''Enable webhook notifications.

        :default: false
        '''
        result = self._values.get("enable_webhook")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def webhook_url(self) -> typing.Optional[builtins.str]:
        '''Webhook URL for notifications Required if enableWebhook is true.'''
        result = self._values.get("webhook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SessionCreateRequest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.SessionDetails",
    jsii_struct_bases=[],
    name_mapping={
        "created_at": "createdAt",
        "enable_account_protection": "enableAccountProtection",
        "enable_message_logging": "enableMessageLogging",
        "enable_webhook": "enableWebhook",
        "id": "id",
        "phone_number": "phoneNumber",
        "session_name": "sessionName",
        "unique_session_id": "uniqueSessionId",
        "updated_at": "updatedAt",
        "user_id": "userId",
        "webhook_url": "webhookUrl",
    },
)
class SessionDetails:
    def __init__(
        self,
        *,
        created_at: builtins.str,
        enable_account_protection: builtins.bool,
        enable_message_logging: builtins.bool,
        enable_webhook: builtins.bool,
        id: builtins.str,
        phone_number: builtins.str,
        session_name: builtins.str,
        unique_session_id: builtins.str,
        updated_at: builtins.str,
        user_id: builtins.str,
        webhook_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Session details.

        :param created_at: Creation timestamp.
        :param enable_account_protection: Session configuration flags.
        :param enable_message_logging: 
        :param enable_webhook: 
        :param id: MongoDB ID of the session.
        :param phone_number: Phone number associated with the session.
        :param session_name: Name of the session.
        :param unique_session_id: Unique session identifier.
        :param updated_at: Last update timestamp.
        :param user_id: User ID who owns the session.
        :param webhook_url: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__596f395204ab95febe6f3697a1d4c0d5942a1dfe1e6f52a0af2b14e28390e61b)
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument enable_account_protection", value=enable_account_protection, expected_type=type_hints["enable_account_protection"])
            check_type(argname="argument enable_message_logging", value=enable_message_logging, expected_type=type_hints["enable_message_logging"])
            check_type(argname="argument enable_webhook", value=enable_webhook, expected_type=type_hints["enable_webhook"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument phone_number", value=phone_number, expected_type=type_hints["phone_number"])
            check_type(argname="argument session_name", value=session_name, expected_type=type_hints["session_name"])
            check_type(argname="argument unique_session_id", value=unique_session_id, expected_type=type_hints["unique_session_id"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
            check_type(argname="argument webhook_url", value=webhook_url, expected_type=type_hints["webhook_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "created_at": created_at,
            "enable_account_protection": enable_account_protection,
            "enable_message_logging": enable_message_logging,
            "enable_webhook": enable_webhook,
            "id": id,
            "phone_number": phone_number,
            "session_name": session_name,
            "unique_session_id": unique_session_id,
            "updated_at": updated_at,
            "user_id": user_id,
        }
        if webhook_url is not None:
            self._values["webhook_url"] = webhook_url

    @builtins.property
    def created_at(self) -> builtins.str:
        '''Creation timestamp.'''
        result = self._values.get("created_at")
        assert result is not None, "Required property 'created_at' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_account_protection(self) -> builtins.bool:
        '''Session configuration flags.'''
        result = self._values.get("enable_account_protection")
        assert result is not None, "Required property 'enable_account_protection' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def enable_message_logging(self) -> builtins.bool:
        result = self._values.get("enable_message_logging")
        assert result is not None, "Required property 'enable_message_logging' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def enable_webhook(self) -> builtins.bool:
        result = self._values.get("enable_webhook")
        assert result is not None, "Required property 'enable_webhook' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''MongoDB ID of the session.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def phone_number(self) -> builtins.str:
        '''Phone number associated with the session.'''
        result = self._values.get("phone_number")
        assert result is not None, "Required property 'phone_number' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def session_name(self) -> builtins.str:
        '''Name of the session.'''
        result = self._values.get("session_name")
        assert result is not None, "Required property 'session_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def unique_session_id(self) -> builtins.str:
        '''Unique session identifier.'''
        result = self._values.get("unique_session_id")
        assert result is not None, "Required property 'unique_session_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def updated_at(self) -> builtins.str:
        '''Last update timestamp.'''
        result = self._values.get("updated_at")
        assert result is not None, "Required property 'updated_at' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> builtins.str:
        '''User ID who owns the session.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def webhook_url(self) -> typing.Optional[builtins.str]:
        result = self._values.get("webhook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SessionDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.SessionListItem",
    jsii_struct_bases=[],
    name_mapping={"downstream": "downstream", "session": "session"},
)
class SessionListItem:
    def __init__(
        self,
        *,
        downstream: typing.Union[DownstreamInfo, typing.Dict[builtins.str, typing.Any]],
        session: typing.Union[SessionDetails, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''Session information from getAllSessions.

        :param downstream: Downstream connection information.
        :param session: Session details.
        '''
        if isinstance(downstream, dict):
            downstream = DownstreamInfo(**downstream)
        if isinstance(session, dict):
            session = SessionDetails(**session)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__253a32a9275ecf9e72bcf1f2b75cf11a6a77a921015a702c79b2bfc420b72ef5)
            check_type(argname="argument downstream", value=downstream, expected_type=type_hints["downstream"])
            check_type(argname="argument session", value=session, expected_type=type_hints["session"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "downstream": downstream,
            "session": session,
        }

    @builtins.property
    def downstream(self) -> DownstreamInfo:
        '''Downstream connection information.'''
        result = self._values.get("downstream")
        assert result is not None, "Required property 'downstream' is missing"
        return typing.cast(DownstreamInfo, result)

    @builtins.property
    def session(self) -> SessionDetails:
        '''Session details.'''
        result = self._values.get("session")
        assert result is not None, "Required property 'session' is missing"
        return typing.cast(SessionDetails, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SessionListItem(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.SessionMetadata",
    jsii_struct_bases=[],
    name_mapping={"user_email": "userEmail", "user_id": "userId"},
)
class SessionMetadata:
    def __init__(self, *, user_email: builtins.str, user_id: builtins.str) -> None:
        '''
        :param user_email: 
        :param user_id: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07c4740974554c0849a34dbedfa991994373e666f12451f52bdcd86b56796bfb)
            check_type(argname="argument user_email", value=user_email, expected_type=type_hints["user_email"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "user_email": user_email,
            "user_id": user_id,
        }

    @builtins.property
    def user_email(self) -> builtins.str:
        result = self._values.get("user_email")
        assert result is not None, "Required property 'user_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> builtins.str:
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SessionMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WasendClient(metaclass=jsii.JSIIMeta, jsii_type="@wasend/core.WasendClient"):
    '''Main Wasend SDK Client.

    This class provides access to the Wasend API for sending messages,
    managing contacts, and other messaging operations.

    Example::

        const client = new WasendClient({
          apiKey: 'your-api-key'
        });
        
        const result = await client.sendMessage({
          to: '+1234567890',
          content: 'Hello, World!'
        });
    '''

    def __init__(
        self,
        *,
        api_key: builtins.str,
        base_url: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Creates a new Wasend client instance.

        :param api_key: The API key for authentication.
        :param base_url: The base URL for the API (optional). Default: https://api.wasend.dev
        :param timeout: Request timeout in milliseconds. Default: 30000
        '''
        config = WasendConfig(api_key=api_key, base_url=base_url, timeout=timeout)

        jsii.create(self.__class__, self, [config])

    @jsii.member(jsii_name="createSession")
    def create_session(
        self,
        *,
        phone_number: builtins.str,
        session_name: builtins.str,
        enable_account_protection: typing.Optional[builtins.bool] = None,
        enable_message_logging: typing.Optional[builtins.bool] = None,
        enable_webhook: typing.Optional[builtins.bool] = None,
        webhook_url: typing.Optional[builtins.str] = None,
    ) -> "Session":
        '''
        :param phone_number: Phone number for the WhatsApp session.
        :param session_name: Name of the session.
        :param enable_account_protection: Enable account protection features. Default: false
        :param enable_message_logging: Enable message logging. Default: false
        :param enable_webhook: Enable webhook notifications. Default: false
        :param webhook_url: Webhook URL for notifications Required if enableWebhook is true.
        '''
        request = SessionCreateRequest(
            phone_number=phone_number,
            session_name=session_name,
            enable_account_protection=enable_account_protection,
            enable_message_logging=enable_message_logging,
            enable_webhook=enable_webhook,
            webhook_url=webhook_url,
        )

        return typing.cast("Session", jsii.ainvoke(self, "createSession", [request]))

    @jsii.member(jsii_name="deleteSession")
    def delete_session(self, session_id: builtins.str) -> None:
        '''
        :param session_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b81b617d22cf593cff9ddd2976e6f0737bcab6b6cbfd35d40b731b45e7f5210)
            check_type(argname="argument session_id", value=session_id, expected_type=type_hints["session_id"])
        return typing.cast(None, jsii.ainvoke(self, "deleteSession", [session_id]))

    @jsii.member(jsii_name="getMessage")
    def get_message(self, message_id: builtins.str) -> ApiResponse:
        '''Get message by ID.

        :param message_id: - The ID of the message to retrieve.

        :return: Promise resolving to the API response
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cb1dc5792b15a5416b556e58d46fc39554d89dbc043723fca120ccd8c6d7a24)
            check_type(argname="argument message_id", value=message_id, expected_type=type_hints["message_id"])
        return typing.cast(ApiResponse, jsii.ainvoke(self, "getMessage", [message_id]))

    @jsii.member(jsii_name="restartSession")
    def restart_session(self, session_id: builtins.str) -> "Session":
        '''
        :param session_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__434c60505ee2fb2a5457c0dbf03cd3dfeaefd14bed60b513aaefc899f45188c2)
            check_type(argname="argument session_id", value=session_id, expected_type=type_hints["session_id"])
        return typing.cast("Session", jsii.ainvoke(self, "restartSession", [session_id]))

    @jsii.member(jsii_name="retrieveAccount")
    def retrieve_account(self) -> ApiResponse:
        '''Get account information.

        :return: Promise resolving to the API response
        '''
        return typing.cast(ApiResponse, jsii.ainvoke(self, "retrieveAccount", []))

    @jsii.member(jsii_name="retrieveAllSessions")
    def retrieve_all_sessions(self) -> GetAllSessionsResponse:
        return typing.cast(GetAllSessionsResponse, jsii.ainvoke(self, "retrieveAllSessions", []))

    @jsii.member(jsii_name="retrieveConfig")
    def retrieve_config(self) -> "WasendConfigInfo":
        '''Get the current configuration.

        :return: The configuration object (without sensitive data)
        '''
        return typing.cast("WasendConfigInfo", jsii.invoke(self, "retrieveConfig", []))

    @jsii.member(jsii_name="retrieveQRCode")
    def retrieve_qr_code(self, session_id: builtins.str) -> QRCodeResponse:
        '''
        :param session_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28c5d954ff13b65e026a7d45c6cb568a11d7bcc2d8c09e6c7e2b6d6364b1104c)
            check_type(argname="argument session_id", value=session_id, expected_type=type_hints["session_id"])
        return typing.cast(QRCodeResponse, jsii.ainvoke(self, "retrieveQRCode", [session_id]))

    @jsii.member(jsii_name="retrieveSessionInfo")
    def retrieve_session_info(self, session_id: builtins.str) -> "Session":
        '''
        :param session_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0df4545c26c4a54c2feea4d8159760885691ec730352cae801811b0e3276ec21)
            check_type(argname="argument session_id", value=session_id, expected_type=type_hints["session_id"])
        return typing.cast("Session", jsii.ainvoke(self, "retrieveSessionInfo", [session_id]))

    @jsii.member(jsii_name="sendMessage")
    def send_message(self, *, content: builtins.str, to: builtins.str) -> ApiResponse:
        '''Send a message to a recipient.

        :param content: The content of the message.
        :param to: The recipient of the message.

        :return: Promise resolving to the API response
        '''
        request = MessageRequest(content=content, to=to)

        return typing.cast(ApiResponse, jsii.ainvoke(self, "sendMessage", [request]))

    @jsii.member(jsii_name="startSession")
    def start_session(self, session_id: builtins.str) -> "Session":
        '''
        :param session_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa7a8584f39c683cf7a8b0b493cff8b738a07457858bf3cd19b6c31a06e322f5)
            check_type(argname="argument session_id", value=session_id, expected_type=type_hints["session_id"])
        return typing.cast("Session", jsii.ainvoke(self, "startSession", [session_id]))

    @jsii.member(jsii_name="stopSession")
    def stop_session(self, session_id: builtins.str) -> "Session":
        '''
        :param session_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90776ed81605470091e6ac1e31d09ac72b2c7b36b5504d37ae9ba1995f67c193)
            check_type(argname="argument session_id", value=session_id, expected_type=type_hints["session_id"])
        return typing.cast("Session", jsii.ainvoke(self, "stopSession", [session_id]))


@jsii.data_type(
    jsii_type="@wasend/core.WasendConfig",
    jsii_struct_bases=[],
    name_mapping={"api_key": "apiKey", "base_url": "baseUrl", "timeout": "timeout"},
)
class WasendConfig:
    def __init__(
        self,
        *,
        api_key: builtins.str,
        base_url: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Configuration options for the Wasend SDK.

        :param api_key: The API key for authentication.
        :param base_url: The base URL for the API (optional). Default: https://api.wasend.dev
        :param timeout: Request timeout in milliseconds. Default: 30000
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c206f9f03c1e9230f7c6c5569fcc5de78f0c947a9e73ad39ca3b1ff4c771d2c)
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_key": api_key,
        }
        if base_url is not None:
            self._values["base_url"] = base_url
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def api_key(self) -> builtins.str:
        '''The API key for authentication.'''
        result = self._values.get("api_key")
        assert result is not None, "Required property 'api_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def base_url(self) -> typing.Optional[builtins.str]:
        '''The base URL for the API (optional).

        :default: https://api.wasend.dev
        '''
        result = self._values.get("base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''Request timeout in milliseconds.

        :default: 30000
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WasendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@wasend/core.WasendConfigInfo",
    jsii_struct_bases=[],
    name_mapping={"base_url": "baseUrl", "timeout": "timeout"},
)
class WasendConfigInfo:
    def __init__(
        self,
        *,
        base_url: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Configuration information (without sensitive data).

        :param base_url: The base URL for the API.
        :param timeout: Request timeout in milliseconds.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6abbc9d87deb2b837793c948e1cf709fe5599235bd5573df1224f4163f2401ad)
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if base_url is not None:
            self._values["base_url"] = base_url
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def base_url(self) -> typing.Optional[builtins.str]:
        '''The base URL for the API.'''
        result = self._values.get("base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''Request timeout in milliseconds.'''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WasendConfigInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WasendUtils(metaclass=jsii.JSIIMeta, jsii_type="@wasend/core.WasendUtils"):
    '''Utility functions for the Wasend SDK.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="formatPhoneNumber")
    @builtins.classmethod
    def format_phone_number(
        cls,
        phone_number: builtins.str,
        country_code: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''Format a phone number to international format.

        :param phone_number: - The phone number to format.
        :param country_code: - Optional country code to use.

        :return: Formatted phone number
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eec89eaaa50e420d927618815b182bd6b5ce4b4a016f10a5e4b0ccc37fc905be)
            check_type(argname="argument phone_number", value=phone_number, expected_type=type_hints["phone_number"])
            check_type(argname="argument country_code", value=country_code, expected_type=type_hints["country_code"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "formatPhoneNumber", [phone_number, country_code]))

    @jsii.member(jsii_name="isValidPhoneNumber")
    @builtins.classmethod
    def is_valid_phone_number(cls, phone_number: builtins.str) -> builtins.bool:
        '''Check if a phone number is valid.

        :param phone_number: - The phone number to validate.

        :return: Whether the phone number is valid
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f3e44e026e6ad10ba5cef7676e8b8f792085bec1680d62137a198b09822712a)
            check_type(argname="argument phone_number", value=phone_number, expected_type=type_hints["phone_number"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isValidPhoneNumber", [phone_number]))


@jsii.data_type(
    jsii_type="@wasend/core.Session",
    jsii_struct_bases=[SessionDetails],
    name_mapping={
        "created_at": "createdAt",
        "enable_account_protection": "enableAccountProtection",
        "enable_message_logging": "enableMessageLogging",
        "enable_webhook": "enableWebhook",
        "id": "id",
        "phone_number": "phoneNumber",
        "session_name": "sessionName",
        "unique_session_id": "uniqueSessionId",
        "updated_at": "updatedAt",
        "user_id": "userId",
        "webhook_url": "webhookUrl",
        "config": "config",
        "engine": "engine",
        "name": "name",
        "status": "status",
    },
)
class Session(SessionDetails):
    def __init__(
        self,
        *,
        created_at: builtins.str,
        enable_account_protection: builtins.bool,
        enable_message_logging: builtins.bool,
        enable_webhook: builtins.bool,
        id: builtins.str,
        phone_number: builtins.str,
        session_name: builtins.str,
        unique_session_id: builtins.str,
        updated_at: builtins.str,
        user_id: builtins.str,
        webhook_url: typing.Optional[builtins.str] = None,
        config: typing.Union[SessionConfig, typing.Dict[builtins.str, typing.Any]],
        engine: typing.Union[EngineStatus, typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        status: builtins.str,
    ) -> None:
        '''Session information from createSession and other operations.

        :param created_at: Creation timestamp.
        :param enable_account_protection: Session configuration flags.
        :param enable_message_logging: 
        :param enable_webhook: 
        :param id: MongoDB ID of the session.
        :param phone_number: Phone number associated with the session.
        :param session_name: Name of the session.
        :param unique_session_id: Unique session identifier.
        :param updated_at: Last update timestamp.
        :param user_id: User ID who owns the session.
        :param webhook_url: 
        :param config: Session configuration.
        :param engine: Engine status information.
        :param name: Name of the session.
        :param status: Current status of the session.
        '''
        if isinstance(config, dict):
            config = SessionConfig(**config)
        if isinstance(engine, dict):
            engine = EngineStatus(**engine)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3d85e74d62c2d977dab7cc527e9efb8b60c3e669b984e32b30b46f61ca261fa)
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument enable_account_protection", value=enable_account_protection, expected_type=type_hints["enable_account_protection"])
            check_type(argname="argument enable_message_logging", value=enable_message_logging, expected_type=type_hints["enable_message_logging"])
            check_type(argname="argument enable_webhook", value=enable_webhook, expected_type=type_hints["enable_webhook"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument phone_number", value=phone_number, expected_type=type_hints["phone_number"])
            check_type(argname="argument session_name", value=session_name, expected_type=type_hints["session_name"])
            check_type(argname="argument unique_session_id", value=unique_session_id, expected_type=type_hints["unique_session_id"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
            check_type(argname="argument webhook_url", value=webhook_url, expected_type=type_hints["webhook_url"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "created_at": created_at,
            "enable_account_protection": enable_account_protection,
            "enable_message_logging": enable_message_logging,
            "enable_webhook": enable_webhook,
            "id": id,
            "phone_number": phone_number,
            "session_name": session_name,
            "unique_session_id": unique_session_id,
            "updated_at": updated_at,
            "user_id": user_id,
            "config": config,
            "engine": engine,
            "name": name,
            "status": status,
        }
        if webhook_url is not None:
            self._values["webhook_url"] = webhook_url

    @builtins.property
    def created_at(self) -> builtins.str:
        '''Creation timestamp.'''
        result = self._values.get("created_at")
        assert result is not None, "Required property 'created_at' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_account_protection(self) -> builtins.bool:
        '''Session configuration flags.'''
        result = self._values.get("enable_account_protection")
        assert result is not None, "Required property 'enable_account_protection' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def enable_message_logging(self) -> builtins.bool:
        result = self._values.get("enable_message_logging")
        assert result is not None, "Required property 'enable_message_logging' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def enable_webhook(self) -> builtins.bool:
        result = self._values.get("enable_webhook")
        assert result is not None, "Required property 'enable_webhook' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''MongoDB ID of the session.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def phone_number(self) -> builtins.str:
        '''Phone number associated with the session.'''
        result = self._values.get("phone_number")
        assert result is not None, "Required property 'phone_number' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def session_name(self) -> builtins.str:
        '''Name of the session.'''
        result = self._values.get("session_name")
        assert result is not None, "Required property 'session_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def unique_session_id(self) -> builtins.str:
        '''Unique session identifier.'''
        result = self._values.get("unique_session_id")
        assert result is not None, "Required property 'unique_session_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def updated_at(self) -> builtins.str:
        '''Last update timestamp.'''
        result = self._values.get("updated_at")
        assert result is not None, "Required property 'updated_at' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> builtins.str:
        '''User ID who owns the session.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def webhook_url(self) -> typing.Optional[builtins.str]:
        result = self._values.get("webhook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config(self) -> SessionConfig:
        '''Session configuration.'''
        result = self._values.get("config")
        assert result is not None, "Required property 'config' is missing"
        return typing.cast(SessionConfig, result)

    @builtins.property
    def engine(self) -> EngineStatus:
        '''Engine status information.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(EngineStatus, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the session.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status(self) -> builtins.str:
        '''Current status of the session.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Session(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccountInfo",
    "ApiResponse",
    "DownstreamInfo",
    "EngineStatus",
    "GetAllSessionsResponse",
    "GowsStatus",
    "GrpcStatus",
    "Message",
    "MessageRequest",
    "NowebConfig",
    "NowebStoreConfig",
    "QRCodeResponse",
    "Session",
    "SessionConfig",
    "SessionCreateRequest",
    "SessionDetails",
    "SessionListItem",
    "SessionMetadata",
    "WasendClient",
    "WasendConfig",
    "WasendConfigInfo",
    "WasendUtils",
]

publication.publish()

def _typecheckingstub__b8d187f8daf4945ee8cc7af4c965fbd16ceba9a4a4f1a826ace5438a45da1cd0(
    *,
    id: builtins.str,
    name: builtins.str,
    plan: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f5feba71406aa1ad99458c7cdc2a9f785cd020e1fbbd5a6830e52fd8bb2382(
    *,
    success: builtins.bool,
    data: typing.Any = None,
    error: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e85038298b8fa1b5985855072c2560ca953a48eea4a7ee8b9f750e8bc6f62348(
    *,
    config: typing.Union[SessionConfig, typing.Dict[builtins.str, typing.Any]],
    engine: typing.Union[EngineStatus, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62f98c4efad3df7d9dcd0fbf647c894254a448f6718f0c1fad58962182024475(
    *,
    gows: typing.Union[GowsStatus, typing.Dict[builtins.str, typing.Any]],
    grpc: typing.Union[GrpcStatus, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09647a94e3d8e4aee98f4628c3fa572a7d308b6f12281833bf5a01c156dec696(
    *,
    sessions: typing.Sequence[typing.Union[SessionListItem, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c788395f63b322df62cfa06c64f225e1401e968d5af857d8143e86d9b74616(
    *,
    connected: builtins.bool,
    found: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a90498c82c9829383ee4faed719fa2d55e4aaaa0a02c2c7519ed1097813a50e6(
    *,
    client: builtins.str,
    stream: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e6ddabade18cb6b127a9542093b14870224ca085a4fedc56304aeee1c2f06ce(
    *,
    content: builtins.str,
    id: builtins.str,
    sent_at: builtins.str,
    status: builtins.str,
    to: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa2d4015027c18549dff3d305605433dfdca504013c7fd0895520c8d64d08e82(
    *,
    content: builtins.str,
    to: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1d9acc660dd7af1a46bcbe0beab4ac7f79e0cb52e2e591c905cb18a2e402a31(
    *,
    mark_online: builtins.bool,
    store: typing.Union[NowebStoreConfig, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3504aad6bb01adf6b4e052cec8a4b4630e3f6d4463e67757a39a236969ffb0c8(
    *,
    enabled: builtins.bool,
    full_sync: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96354063aeb190a9953a739f8ddd730b166f0b989d0a398486425665f25137a3(
    *,
    data: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4bda00ff00f4da8f5d020b9ae62f84aef28dfe5100c707bc597e0d613a8ca00(
    *,
    debug: builtins.bool,
    metadata: typing.Union[SessionMetadata, typing.Dict[builtins.str, typing.Any]],
    noweb: typing.Union[NowebConfig, typing.Dict[builtins.str, typing.Any]],
    proxy: typing.Any,
    webhooks: typing.Sequence[typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e3cdcf8dd89941a7ff518341872e1a93509aae9d708132cd86835fcac559df4(
    *,
    phone_number: builtins.str,
    session_name: builtins.str,
    enable_account_protection: typing.Optional[builtins.bool] = None,
    enable_message_logging: typing.Optional[builtins.bool] = None,
    enable_webhook: typing.Optional[builtins.bool] = None,
    webhook_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__596f395204ab95febe6f3697a1d4c0d5942a1dfe1e6f52a0af2b14e28390e61b(
    *,
    created_at: builtins.str,
    enable_account_protection: builtins.bool,
    enable_message_logging: builtins.bool,
    enable_webhook: builtins.bool,
    id: builtins.str,
    phone_number: builtins.str,
    session_name: builtins.str,
    unique_session_id: builtins.str,
    updated_at: builtins.str,
    user_id: builtins.str,
    webhook_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__253a32a9275ecf9e72bcf1f2b75cf11a6a77a921015a702c79b2bfc420b72ef5(
    *,
    downstream: typing.Union[DownstreamInfo, typing.Dict[builtins.str, typing.Any]],
    session: typing.Union[SessionDetails, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07c4740974554c0849a34dbedfa991994373e666f12451f52bdcd86b56796bfb(
    *,
    user_email: builtins.str,
    user_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b81b617d22cf593cff9ddd2976e6f0737bcab6b6cbfd35d40b731b45e7f5210(
    session_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cb1dc5792b15a5416b556e58d46fc39554d89dbc043723fca120ccd8c6d7a24(
    message_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__434c60505ee2fb2a5457c0dbf03cd3dfeaefd14bed60b513aaefc899f45188c2(
    session_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c5d954ff13b65e026a7d45c6cb568a11d7bcc2d8c09e6c7e2b6d6364b1104c(
    session_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0df4545c26c4a54c2feea4d8159760885691ec730352cae801811b0e3276ec21(
    session_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa7a8584f39c683cf7a8b0b493cff8b738a07457858bf3cd19b6c31a06e322f5(
    session_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90776ed81605470091e6ac1e31d09ac72b2c7b36b5504d37ae9ba1995f67c193(
    session_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c206f9f03c1e9230f7c6c5569fcc5de78f0c947a9e73ad39ca3b1ff4c771d2c(
    *,
    api_key: builtins.str,
    base_url: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6abbc9d87deb2b837793c948e1cf709fe5599235bd5573df1224f4163f2401ad(
    *,
    base_url: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eec89eaaa50e420d927618815b182bd6b5ce4b4a016f10a5e4b0ccc37fc905be(
    phone_number: builtins.str,
    country_code: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f3e44e026e6ad10ba5cef7676e8b8f792085bec1680d62137a198b09822712a(
    phone_number: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3d85e74d62c2d977dab7cc527e9efb8b60c3e669b984e32b30b46f61ca261fa(
    *,
    created_at: builtins.str,
    enable_account_protection: builtins.bool,
    enable_message_logging: builtins.bool,
    enable_webhook: builtins.bool,
    id: builtins.str,
    phone_number: builtins.str,
    session_name: builtins.str,
    unique_session_id: builtins.str,
    updated_at: builtins.str,
    user_id: builtins.str,
    webhook_url: typing.Optional[builtins.str] = None,
    config: typing.Union[SessionConfig, typing.Dict[builtins.str, typing.Any]],
    engine: typing.Union[EngineStatus, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
