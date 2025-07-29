import random
import typing

from datetime import datetime
from enum import IntEnum

if typing.TYPE_CHECKING:
  from .shape import ShapeBase


MISSING = object()

class ABCBase:
  """Base class for objects in this module
  
  .. container:: operations
  
      .. describe:: x == y
      
          Checks if the instance is same as other
          
      .. describe:: x != y
      
          Checks if the instance is not same as other

  """
  def __init__(self, id: str = MISSING):
    self.id = id

  @property
  def id(self) -> str:
    return self.__id

  @id.setter
  def id(self, value: str):
    if value is MISSING:
      value = str(random.randint(1,9))
      value += "".join(str(random.randint(0,9)) for _ in range(9))
      
    self.__id = value

  @classmethod
  def new(cls): return cls()
  
  def __eq__(self, o):
    if not hasattr(o, "id"): return False
    return self.id == o.id and self.__class__ == o.__class__

  def __ne__(self, o):
    return not self == o

class ShapeUser(ABCBase):
  """User for shape
  
  Parameters
  -----------
  id: Optional[:class:`~str`]
    ID of the user
  """

class ShapeChannel(ABCBase):
  """Channel for shape. Used for context
  
  Parameters
  -----------
  id: Optional[:class:`~str`]
    ID of the channel
  """


class ContentType(IntEnum):
  """Enumeration for message content.
  
  Attributes
  -----------
  text:
    for text messages
  audio:
    for audio messages
  image:
    for image messages
  """
  text:  int = 1
  audio: int = 2
  image: int = 3
  
  def __repr__(self) -> str:
    return f"<ContentType 'shapesinc.ContentType.{self.name}'>"
    
  __str__ = __repr__

class MessageContent(ABCBase):
  """Content of the message
  
  Attributes
  -----------
  content: :class:`~str`
    The content of message if it is text or its URL.
  type: :class:`shapesinc.ContentType`
  """
  def __init__(self, content: str, type: ContentType = ContentType.text):
    self.type = type
    super().__init__(content)

  @property
  def content(self) -> str:
    """Content of the message"""
    return self.id

  @content.setter
  def content(self, value: str):
    self.id = value
    
  @classmethod
  def from_dict(cls, data: dict):
    """Converts json to message content"""
    assert data["type"] in ["image_url", "audio_url", "text"], ValueError("Expected ContentType input")
    
    if data["type"]=="text":
      return cls("text", ContentType.text)
      
    return cls(
      data[data["type"]]["url"],
      ContentType.audio if data["type"] == "audio_url" else ContentType.image
    )
    
  def to_dict(self) -> dict:
    """Converts itself to JSON format"""
    return {
      "type": f"{self.type.name}_url",
      f"{self.type.name}_url": {
        "url": self.content
      }
    } if self.type != ContentType.text else {
      "type": "text",
      "text": self.content
    }
    
  def __eq__(self, o):
    if not super().__eq__(o):
      return False
    if not hasattr(o, "type"): return False
    return self.type == o.type
    
class Message:
  """Message
  
  Attributes
  -----------
  content: typing.List[:class:`shapesinc.MessageContent`]
    Contents of the message.
  role: :class:`~str`
    Role of the author. Default: "user"
  """
  def __init__(self, content: typing.List[MessageContent] = None, role: str = "user"):
    assert content, ValueError("Cannot create empty message!")
    self.content = content
    self.role = role
    
  def __repr__(self) -> str:
    if len(self.content)==1 and self.content[0].type==ContentType.text:
      return self.content[0].content
      
    return super().__repr__()
    
  __str__ = __repr__
  
  def to_dict(self) -> dict:
    """Converts itself into JSON format"""
    return {
      "role": self.role,
      "content": [c.to_dict() for c in self.content]
    }
    
  @classmethod
  def from_dict(cls, data: dict):
    """JSON to :class:`shapesinc.Message`"""
    return cls(
      [MessageContent.from_dict(c) for c in data["content"]] if isinstance(data["content"], list) else [MessageContent(data["content"])],
      data["role"]
    )
    
  @classmethod
  def new(cls, text: str = "", files: dict = {}, role: str = "user"):
    """Simple method to create a new message
    
    Parameters
    -----------
    text: Optional[:class:`~str`]
      The text which is to be sent.
    files: Optional[:class:`~dict`]
      Files which are to be sent.
    role: Optional[:class:`~str`]
      Role of the sender. Default 'user'
      
    Raises
    -------
    ValueError
      Raised when neither text nor files are given.
    """
    assert text or files, ValueError("Cannot create empty message!")
    c = []
    if text:
      c.append(MessageContent(text))
    if files:
      c.extend([MessageContent (f["url"], f["type"]) for f in files])
      
    return cls(c, role)
    
class TypedDict(dict):
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      v = getattr(self, "_parse_"+k, lambda x:x)(v)
      setattr(self, k, v)
      
    super().__init__(**kwargs)

class PromptResponse_Choice(TypedDict):
  """Choice (generated by shape)
  
  Attributes
  -----------
  index: :class:`~int`
    index of the choice
  message: :class:`shapesinc.Message`
    Message
  """
  index: int
  message: Message
  finish_reason: typing.Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
  
  _parse_message = Message.from_dict

class PromptResponse_Usage(TypedDict):
  prompt_tokens: int
  total_tokens: int
  completion_tokens_details: typing.Optional[dict] = None
  prompt_tokens_details: typing.Optional[dict] = None

class PromptResponse(TypedDict):
  """Response generated by Shape
  
  Attributes
  -----------
  id: :class:`~str`
    ID of the request
  model: :class:`~str`
    name of model (shape)
  created: :class:`~datetime.datetime`
    Time when the response was generated
  choices: typing.List[:class:`shapesinc.abc.PromptResponse_Choice]
    list of choices generated by shape.
  shape: Union[:class:`shapesinc.Shape`, :class:`shapesinc.AsyncShape`]
    Shape which genrated the response.
  """
  id: str
  model: str
  object: typing.Literal["chat.completion"]
  usage: typing.Optional[PromptResponse_Usage] = None
  created: datetime
  choices: typing.List[PromptResponse_Choice]
  
  if typing.TYPE_CHECKING:
    shape: ShapeBase
  
  _parse_created = datetime.fromtimestamp
  _parse_choices = lambda _, cs: [PromptResponse_Choice(**c) for c in cs]
  _parse_usage = lambda _, u: PromptResponse_Usage(**u)


class APIError(Exception):
  """Base class for API exceptions"""
  def __init__(self, data: dict):
    self.message = data["error"]["message"]
    self.data = data
    super().__init__(data["error"]["message"])
    
class RateLimitError(APIError):
  """Raised when api is being ratelimited"""
