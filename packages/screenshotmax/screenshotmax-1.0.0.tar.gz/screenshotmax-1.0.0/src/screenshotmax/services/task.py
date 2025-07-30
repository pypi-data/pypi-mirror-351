from typing import Any, Dict
from ..client import APIClient


class TaskService:
  path = "/v1/tasks"

  def __init__(self, client: APIClient) -> None:
    self.client = client

  def get_tasks(self) -> str:
    data, _ = self.client.get(self.path)
    if isinstance(data, bytes):
      return data.decode()
    return data

  def get_task(self, task_id: int) -> str:
    data, _ = self.client.get(f"{self.path}/{task_id}")
    if isinstance(data, bytes):
      return data.decode()
    return data

  def create_task(self, options: Dict[str, Any]) -> str:
    data, _ = self.client.post(self.path, options)
    if isinstance(data, bytes):
      return data.decode()
    return data

  def delete_task(self, task_id: int) -> Any:
    return self.client.delete(f"{self.path}/{task_id}")

  def update_task(self, task_id: int, options: Dict[str, Any]) -> Any:
    return self.client.patch(f"{self.path}/{task_id}", options)
