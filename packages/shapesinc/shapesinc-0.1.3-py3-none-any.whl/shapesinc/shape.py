import aiohttp
import json
import sys
import typing
import urllib.request as request

from urllib.error import HTTPError

from .__info__ import __version__
from .abc import (
  ShapeUser as User,
  ShapeChannel as Channel,
  Message,
  PromptResponse,
  APIError,
  RateLimitError
)

vi = sys.version_info
PYTHON_VERSION = f"{vi.major}.{vi.minor}.{vi.micro}{vi.releaselevel}{vi.serial}".split("final")[0]

BASE_HTTP_URL = "https://api.shapes.inc/v1"

SYNCHRONOUS_MODELS = {}
ASYNCHRONOUS_MODELS = {}
ACTIVE_MODELS = {
  "SYNCHRONOUS": SYNCHRONOUS_MODELS,
  "ASYNCHRONOUS": ASYNCHRONOUS_MODELS
}

class ShapeBase:
  """
  Base class for creating shapes.
  Parameters
  ------------
  api_key: :class:`~str`
    Your API key for shapes.inc
  username: :class:`~str`
    Username of the shape
    
  Raises
  -------
  RuntimeError
    It is raised when an instance for given username is already created for same environment.
  """
  def __init__(self, api_key: str, username: str):
    assert username not in ACTIVE_MODELS[self.type], RuntimeError(f"An instance ({self.type.lower()}) of model '{username}' has already been created for this environment. Please use that instance instead")
    ACTIVE_MODELS[self.type][username] = self
    self.api_key = api_key
    self.username = username

  @property
  def type(self) -> typing.Literal["SYNCHRONOUS", "ASYNCHRONOUS"]:
    """Tells whether the instance is configured for asynchronous environment or synchronous"""
    raise NotImplementedError

  @property
  def api_key(self) -> str:
    """API key"""
    return self.__api_key

  @api_key.setter
  def api_key(self, value: str):
    self.__api_key = value

  @property
  def model_name(self) -> str:
    """Name of model of your shape"""
    return "shapesinc/"+self.username
    
  def prompt(self, message: Message, user: User = None, channel: Channel = None) -> typing.Union[PromptResponse, typing.Awaitable[PromptResponse]]:
    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }
    if user is not None:
      headers["X-User-Id"] = user.id
    if channel is not None:
      headers["X-Channel-Id"] = channel.id
      
    if isinstance(message, str):
      message=Message.new(message)
    return self.make_request([message.to_dict()], headers)

  def make_request(self, message: typing.List[typing.Dict[str, str]], headers: typing.Dict[str, str]) -> PromptResponse:
    """The method which is implemented to make requests to API

    Raises
    -------
    NotImplementedError
    """
    raise NotImplementedError

class Shape(ShapeBase):
  """Creates a shape for synchronous environment.
  
  It is a subclass of :class:`shapesinc.ShapeBase`

  Parameters
  ------------
  api_key: :class:`~str`
    Your API key for shapes.inc
  username: :class:`~str`
    Username of the shape

  Example
  ---------
  
  .. code-block:: python3
    
      import shapesinc
      shape = shapesinc.Shape("API_KEY", "Myshape")
      
      def run():
        while True:
          q = input(" >>> ")
          print(shape.prompt(q))

  Raises
  -------
  RuntimeError
    It is raised when an instance for given username is already created for same environment.
  """
  type: str = "SYNCHRONOUS"
  
  def prompt(self, *args, **kwargs) -> PromptResponse:
    """Send a prompt through the shape
    
    Parameters
    -----------
    message: Union[:class:`shapesinc.Message`, :class:`~str`]
      The message which is to be sent to the shape. Can be a :class:`shapesinc.Message` or a string.
    user: Optional[:class:`shapesinc.ShapeUser`]
      The user who is sending the message.
    channel: Optional[:class:`shapesinc.ShapeChannel`]
      The channel in which the message is being sent. Used for context.
      
    Returns
    --------
    :class:`shapesinc.PromptResponse`
      The response of the prompt.
    Raises
    -------
    :class:`shapesinc.RateLimitError`
      Error when we get ratelimited
    :class:`shapesinc.APIError`
      Error raised by shapes.inc API.
    """
    return super().prompt(*args, **kwargs)

  def make_request(self, messages: typing.List[typing.Dict[str, str]], headers: typing.Dict[str, str]) -> PromptResponse:
    headers["User-Agent"] = f"Shapes.inc API Wrapper Py using Python/{PYTHON_VERSION} shapesinc-py/{__version__}"
    req = request.Request(
      BASE_HTTP_URL+"/chat/completions",
      data = json.dumps({
        "model": self.model_name,
        "messages": messages
      }).encode(),
      headers = headers
    )
    try:
      req = request.urlopen(req)
    except HTTPError as req:
      res = json.loads(req.read())
      e = RateLimitError if req.code == 429 else APIError
      raise e(res)

    res = json.loads(req.read())
    return PromptResponse(shape=self, **res)


class AsyncShape(ShapeBase):
  """Creates a shape for synchronous environment.
  
  It is a subclass of :class:`shapesinc.ShapeBase`

  Parameters
  ------------
  api_key: :class:`~str`
    Your API key for shapes.inc
  username: :class:`~str`
    Username of the shape

  Example
  ---------
  
  .. code-block:: python3
    
      import shapesinc
      shape = shapesinc.AsyncShape("API_KEY", "Myshape")
      
      async def run():
        while True:
          q = input(" >>> ")
          print(await shape.prompt(q))

  Raises
  -------
  RuntimeError
    It is raised when an instance for given username is already created for same environment.
  """
  type: str = "ASYNCHRONOUS"
  
  async def prompt(self, *args, **kwargs) -> PromptResponse:
    """Send a prompt through the shape
    
    Parameters
    -----------
    message: Union[:class:`shapesinc.Message`, :class:`~str`]
      The message which is to be sent to the shape. Can be a :class:`shapesinc.Message` or a string.
    user: Optional[:class:`shapesinc.ShapeUser`]
      The user who is sending the message.
    channel: Optional[:class:`shapesinc.ShapeChannel`]
      The channel in which the message is being sent. Used for context.
      
    Returns
    --------
    :class:`shapesinc.PromptResponse`
      The response of the prompt.
    Raises
    -------
    :class:`shapesinc.RateLimitError`
      Error when we get ratelimited
    :class:`shapesinc.APIError`
      Error raised by shapes.inc API.
    """
    return await super().prompt(*args, **kwargs)
  async def make_request(self, messages: typing.List[typing.Dict[str, str]], headers: typing.Dict[str, str]) -> PromptResponse:
    async with aiohttp.ClientSession() as ses:
      data = await ses.post(
        BASE_HTTP_URL+"/chat/completions",
        json = {
          "model": self.model_name,
          "messages": messages
        },
        headers = headers
      )
      sc = data.status
      res = await data.json()
      
    if sc == 429:
      raise RateLimitError(res)
    if "error" in res:
      raise APIError(res)
    return PromptResponse(shape=self, **res)


def shape(api_key: str, username: str, *, synchronous: bool = True) -> typing.Union[Shape, AsyncShape]:
  """Creates a new instance for a shape if none exists; otherwise, returns the original instance.

  Parameters
  -----------
  api_key: :class:`~str`
    Your API key for shapes.inc
  username: :class:`~str`
    Username of the shape
  synchronous: Optional[:class:`~bool`]
    Whether the instance is to be configured for synchronous environment or asynchronous. Default: False
  
  Returns
  --------
  :class:`shapesinc.Shape`
    If the instance is configured for synchronous environment.
  :class:`shapesinc.AsyncShape`
    If the instance is configured for asynchronous environment.
  """
  type = "ASYNCHRONOUS" if not synchronous else "SYNCHRONOUS"
  model = ACTIVE_MODELS[type].get(username)
  if model:
    return model
    
  if synchronous:
    return Shape(api_key, username)
    
  return AsyncShape(api_key, username)
