import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Type, TypeVar, Optional

T = TypeVar("T", bound=BaseModel)


def loadEnv(pydanticModel: Type[T], dotenvPath: Optional[str] = None) -> T:
    """
    Load environment variables into a given Pydantic model.

    Args:
        pydanticModel (Type[T]): A Pydantic model class.
        dotenvPath (Optional[str]): Optional path to a .env file.

    Returns:
        T: An instance of the model populated with environment variables.
    """
    load_dotenv(dotenv_path=dotenvPath, override=True)

    env_values = {
        field_name: os.getenv(field_name)
        for field_name in pydanticModel.model_fields.keys()
    }

    return pydanticModel(**env_values)
