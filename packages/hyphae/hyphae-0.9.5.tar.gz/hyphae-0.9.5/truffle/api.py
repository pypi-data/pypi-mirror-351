from . import platform
from .platform import SDK_SOCK
from .common import get_logger


import grpc
import json
import typing


logger = get_logger()

#02.01.25
#this sucks!!! derek fucked it
# should just be methods, and inference needs really good abstraction
#client can be a fucking global set by runtime
# fix this, fix trufflefile, and add client runtime that validates!

#then CLI and this shit is good to go


class TruffleClient:
    def __init__(self, host=SDK_SOCK):
        self.channel = grpc.insecure_channel(host)
        self.stub = platform.sdk_pb2_grpc.TruffleSDKStub(self.channel)
        self.model_contexts: list[platform.sdk_pb2.Context] = []

    def perplexity_search(
        self,
        query: str,
        model: str = "sonar",
        response_fmt=None,
        system_prompt: str = "",
    ) -> str:
        # https://docs.perplexity.ai/guides/model-cards
        perplexity_models_feb24 = [
            "sonar-reasoning",  # Chat Completion - 127k context length
            "sonar-pro",        # Chat Completion - 200k 
            "sonar",            # Chat Completion - 127k 
        ]
        if model not in perplexity_models_feb24:
            raise ValueError(
                f"Model '{model}' not found in available models [{perplexity_models_feb24}]. See https://docs.perplexity.ai/guides/model-cards"
            )

        PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
        }
        # https://docs.perplexity.ai/guides/structured-outputs
        if response_fmt is not None:
            payload["response_format"] = response_fmt

        # TODO: support everything! they have such a cool API - image return would be insane, and citations!
        # https://docs.perplexity.ai/api-reference/chat-completions
        try:
            request = platform.sdk_pb2.SystemToolRequest(tool_name="perplexity_search")
            request.args["url"] = PERPLEXITY_API_URL
            request.args["payload"] = json.dumps(payload)

            r: platform.sdk_pb2.SystemToolResponse = self.stub.SystemTool(request)
            if r.error:
                raise RuntimeError(f"SystemToolError: {r.error}")

            results = json.loads(r.response)

            return results["choices"][0]["message"]["content"]
        except grpc.RpcError as e:
            raise RuntimeError(f"RPC error: {e.details()}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"JSON error: {e}")

    def get_models(self):
        response: list[platform.sdk_pb2.ModelDescription] = self.stub.GetModels(
            platform.sdk_pb2.GetModelsRequest()
        ).models
        return response

    # WIP - missing ui
    def tool_update(self, message: str):
        try:
            r: platform.sdk_pb2.SDKResponse = self.stub.ToolUpdate(
                platform.sdk_pb2.ToolUpdateRequest(friendly_description=message)
            )
            if r.error:
                raise RuntimeError(f"RPC error: {r.error}")

        except grpc.RpcError as e:
            raise RuntimeError(f"RPC error: {e.details()}")

    # WIP - missing ui
    def ask_user(
        self, message: str, reason: str = "Tool needs input to continue."
    ) -> typing.Dict[str, typing.Union[str, typing.List[str]]]:
        
        try:
            response: platform.sdk_pb2.UserResponse = self.stub.AskUser(
                platform.sdk_pb2.UserRequest(message=message, reason=reason)
            )
            ret = {"response": response.response}
            return ret

        except grpc.RpcError as e:
            raise RuntimeError(f"RPC error: {e.details()}")

    def query_embed(
        self, query: str, documents: typing.List[str]
    ) -> typing.List[typing.Tuple[str, float]]:
        """
        Returns a list of documents sorted by cosine similarity to the query via. text embeddings, which really should include that value. Doh.

        Args:
            query: The query string
            documents: A list of document strings to search

        Returns:
            A list of document strings sorted by cosine similarity to the query from most to least similar

        """
        request = platform.sdk_pb2.EmbedRequest(query=query, documents=documents)
        # i have not tested this
        try:
            response: platform.sdk_pb2.EmbedResponse = self.stub.Embed(request)
            print("Embedding response: ")
            results = []
            if len(response.results) == 0:
                raise ValueError("No results returned")
            for r in response.results:
                print(f"{r.text}: {r.score}")
                results.append((r.text, r.score))
            return results
        except grpc.RpcError as e:
            raise RuntimeError(f"Embed RPC error: {e.details()}")
        except ValueError as e:
            raise RuntimeError(f"Embed Value error: {e}")

    def infer(
        self,
        prompt: str,
        model_id: int = 0,
        system_prompt: str | None = None,
        context_idx: int | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        format_type: str = None,
        schema: str = None,
    ) -> typing.Iterator[str]:
        """
        Make a streaming inference request to the TruffleSDK service.

        Args:
            prompt: The input prompt for generation
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            format_type: Optional response format (TEXT, JSON, EBNF)
            schema: Optional schema for structured output

        Returns:
            Iterator yielding generated tokens
        """
        # TODO: properly handle format stuff
        format_spec = None
        if format_type:
            format_spec = platform.sdk_pb2.GenerateResponseFormat(
                format=platform.sdk_pb2.GenerateResponseFormat.ResponseFormat.Value(
                    f"RESPONSE_{format_type}"
                ),
                schema=schema,
            )

        # Fetch or build the context for the chat
        if context_idx is not None:
            if self.context_idx is not None and system_prompt is not None:
                raise ValueError(
                    "Only pass system_prompt or context_idx, but not both!"
                )
            current_context = self.model_contexts[context_idx]
        else:
            self.model_contexts.append(platform.sdk_pb2.Context())
            current_context: platform.sdk_pb2.Context = self.model_contexts[-1]
            if system_prompt is not None:
                current_context.history.append(
                    platform.sdk_pb2.Content(
                        role=platform.sdk_pb2.Content.ROLE_SYSTEM, content=system_prompt
                    )
                )

        current_context.history.append(
            platform.sdk_pb2.Content(
                role=platform.sdk_pb2.Content.Role.ROLE_USER, content=prompt
            )
        )

        # Create the generation request
        request = platform.sdk_pb2.GenerateRequest(
            model_id=model_id,
            context=current_context,
            max_tokens=max_tokens,
            temperature=temperature,
            fmt=format_spec,
        )

        try:
            # Make the streaming call
            streamed_message = []
            for response in self.stub.Infer(request):
                if response.error:
                    raise RuntimeError(f"Generation error: {response.error}")

                if response.finish_reason:
                    # Handle different finish reasons
                    if (
                        response.finish_reason
                        == platform.sdk_pb2.GenerateFinishReason.FINISH_REASON_ERROR
                    ):
                        raise RuntimeError("Generation terminated with error")
                    elif (
                        response.finish_reason
                        != platform.sdk_pb2.GenerateFinishReason.FINISH_REASON_UNSPECIFIED
                    ):
                        break

                streamed_message.append(response.token)
                yield response.token

            current_context.history.append(
                platform.sdk_pb2.Content(
                    role=platform.sdk_pb2.Content.ROLE_AI,
                    content="".join(streamed_message),
                )
            )

        except grpc.RpcError as e:
            raise RuntimeError(f"RPC error: {e} {e.details()}")


    def _globalvar(self, key:str, value:str = None) -> str:
        if value is not None:
            value = str(value)
        request = platform.sdk_pb2.GlobalsRequest(key=key, value=value)
        logger.debug(f"GlobalsRequest: {request}")
        response: platform.sdk_pb2.GlobalsResponse = self.stub.GlobalVars(request)
        logger.debug(f"GlobalsResponse: {response}")
        return response.value
    def close(self):
        """Close the gRPC channel"""
        self.channel.close()


class TGlobals:
    _reserved = ['set', 'get', 'contains', '_client', '_cache']
    def __init__(self, client: TruffleClient = TruffleClient()):
        self._client = client
        self._cache : typing.Dict[str, bool] = {}
    def __getattr__(self, key: str) -> str: #can throw 
       return self.get(key)
    def __setattr__(self, key: str, value: str) -> None:
        if key in self._reserved:
            super().__setattr__(key, value)   # normal attribute write
            return
        self.set(key, value)
       
    
    def __getitem__(self, key):
        return self.__getattr__(key)
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    def __contains__(self, key: str) -> bool:
        return self.contains(key)
    
    def set(self, key: str, value: str) -> str:
        #returns prev value if set 
        prev = self._client._globalvar(key, value)
        self._cache[key] = True
        return prev
    def contains(self, key: str) -> bool:
        if key in self._cache:
            return True
        try:
            v = self.get(key)
            if v is not None:
                self._cache[key] = True
                return True
        except Exception as e:
            pass
        return False
     
    
    def get(self, key: str) -> str:
        #returns prev value if set 
        return self._client._globalvar(key)
    

