from typing import List, Dict, Union, Optional
from typing import TYPE_CHECKING

import requests

from .authorization import Authorization

if TYPE_CHECKING:
    from typing import List, Dict, Union, Optional


class Perception:
    def __init__(self):
        # Initialize authorization
        self.auth = Authorization()
        self.base_url = f"{self.auth.host}/perception"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_access_token()}"
        }

    def _get_task_result(self, task_id: str) -> Dict:
        """Get the result of a perception task
        
        Args:
            task_id (str): The ID of the task to get results for
        
        Returns:
            Dict: The complete task result containing status and data.
                 The structure of taskResult varies depending on the task type.
                 For detailed response structures, please refer to:
                 https://qj-robots.feishu.cn/wiki/CT5cwncfdi28nEk24vZcOl9Nnye
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        return self._make_get_request(
            endpoint="/open-api/open-apis/app/perception/result",
            params={"task_id": task_id}
        )

    def _poll_task_result(self, task_id: str, timeout: int = 30) -> Dict:
        """Poll for task result until completion or timeout
        
        Args:
            task_id (str): The ID of the task to poll for
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 30.
        
        Returns:
            Dict: The complete task result
        
        Raises:
            TimeoutError: If polling exceeds timeout seconds
        """
        import time
        start_time = time.time()
        while True:
            # Check if polling has exceeded timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(f"{task_id} => Polling exceeded {timeout} seconds timeout")

            # Get task result
            result = self._get_task_result(task_id)

            if result['taskStatus'] == 'SUBMIT_FAILED':
                raise RuntimeError(f"{task_id} => task submit failed,please retry later.")
            # Return if task is complete
            if result['taskStatus'] == 'DONE':
                return result

            # Wait before next poll
            time.sleep(0.01)

    def _validate_image_params(self, image_type: str, depth_url: Optional[str] = None) -> None:
        """Validate image type and depth_url parameters
        
        Args:
            image_type (str): Image type to validate
            depth_url (Optional[str], optional): Depth URL to validate for 3D images
        
        Raises:
            ValueError: If parameters are invalid
        """
        if image_type not in ['2D', '3D']:
            raise ValueError("image_type must be either '2D' or '3D'")

        if image_type == '3D' and not depth_url:
            raise ValueError("depth_url is required for 3D images")

    def _process_object_names(self, object_names: Union[str, List[str]]) -> str:
        """Process object names into comma-separated string
        
        Args:
            object_names (Union[str, List[str]]): Names of objects to process
        
        Returns:
            str: Comma-separated string of object names
        """
        if isinstance(object_names, list):
            return ','.join(object_names)
        return object_names

    def _prepare_request_data(self, image_type: str, image_url: str,
                              object_names: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict:
        """Prepare request data for perception API calls
        
        Args:
            image_type (str): Image type ('2D' or '3D')
            image_url (str): URL of the image
            object_names (Union[str, List[str]]): Names of objects
            depth_url (Optional[str], optional): URL of the depth image
        
        Returns:
            Dict: Prepared request data
        """
        data = {
            "image_type": image_type,
            "image_url": image_url,
            "object_names": self._process_object_names(object_names)
        }

        if depth_url:
            data["depth_url"] = depth_url

        return data

    def _make_post_request(self, endpoint: str, data: Dict) -> Dict:
        """Make POST request to perception API
        
        Args:
            endpoint (str): API endpoint
            data (Dict): Request data
        
        Returns:
            Dict: Response data
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.auth.host}{endpoint}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()

        result = response.json()
        if result["code"] != 0:
            raise Exception(f"API request failed: {result['message']}")

        return result["data"]

    def _make_get_request(self, endpoint: str, params: Dict) -> Dict:
        """Make GET request to perception API
        
        Args:
            endpoint (str): API endpoint
            params (Dict): Request parameters
        
        Returns:
            Dict: Response data
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.auth.host}{endpoint}"
        response = requests.get(url, params=params)

        result = response.json()
        if result["code"] != 0:
            raise Exception(f"API request failed: {result['message']}")

        return result["data"]

    def check_image(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                    depth_url: Optional[str] = None) -> Dict:
        """Check image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be checked
            object_names (Union[str, List[str]]): Names of objects to detect, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 For detailed response structures, please refer to:
                 https://qj-robots.feishu.cn/wiki/CT5cwncfdi28nEk24vZcOl9Nnye
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/check",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def split_image(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                    depth_url: Optional[str] = None) -> Dict:
        """Split objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to segment, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - masks: List of mask objects containing maskImage URL and maskData
                 - croppedImagesListBbox: List of cropped image URLs
                 - labels: List of detected object labels
                 - scores: List of confidence scores
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/split",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def props_describe(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                       questions: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict:
        """Get detailed property descriptions of objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to describe, can be a comma-separated string or a list of strings
            questions (Union[str, List[str]]): Questions about object properties, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - labels: List of detected object labels
                 - scores: List of confidence scores
                 - answers: List of property description objects
                 - questions: List of property questions
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Add questions to request data
        if isinstance(questions, list):
            data["questions"] = ','.join(questions)
        else:
            data["questions"] = questions

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/props-describe",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def angle_prediction(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                         depth_url: Optional[str] = None) -> Dict:
        """Predict angles of objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to predict angles for, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - angles: List of angle objects containing angle value and corner points
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - labels: List of detected object labels
                 - scores: List of confidence scores
                 - croppedImagesListAngle: List of cropped image URLs
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/angle-prediction",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def key_point_prediction(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                             depth_url: Optional[str] = None) -> Dict:
        """Predict key points of objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to predict key points for, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - points: List of point objects containing:
                   - pointBoxes: List of point box coordinates [x1,y1,x2,y2]
                   - pointLabels: List of point labels
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - labels: List of detected object labels
                 - scores: List of confidence scores
                 - croppedImagesListPoint: List of cropped image URLs
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/key-point-prediction",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def grab_point_prediction(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                              depth_url: Optional[str] = None) -> Dict:
        """Predict grab points of objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to predict grab points for, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - grasps: List of grasp objects containing:
                   - graspAngle: Angle of the grasp
                   - graspPoint: List of grasp point coordinates [x,y]
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - labels: List of detected object labels
                 - scores: List of confidence scores
                 - croppedImagesListGrasp: List of cropped image URLs
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/grab-point-prediction",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def full_perception(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                        questions: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict:
        """Submit a comprehensive perception task that includes all 6 perception functions
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to analyze, can be a comma-separated string or a list of strings
            questions (Union[str, List[str]]): Questions about object properties, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - angles: List of angle objects containing angle value and corner points
                 - angles3D: List of 3D angle information
                 - answers: List of property description objects
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - croppedImagesListAngle: List of angle-based cropped image URLs
                 - croppedImagesListBbox: List of bbox-based cropped image URLs
                 - croppedImagesListGrasp: List of grasp-based cropped image URLs
                 - croppedImagesListPoint: List of point-based cropped image URLs
                 - croppedImagesListSegment: List of segment-based cropped image URLs
                 - grasps: List of grasp objects containing angle, depth, height, width etc.
                 - labels: List of detected object labels
                 - maskImage: List of mask image download URLs
                 - maskData: List of mask data download URLs
                 - points: List of point objects containing coordinates and labels
                 - questions: List of property questions
                 - scores: List of confidence scores
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Add questions to request data
        if isinstance(questions, list):
            data["questions"] = ','.join(questions)
        else:
            data["questions"] = questions

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/full",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])
