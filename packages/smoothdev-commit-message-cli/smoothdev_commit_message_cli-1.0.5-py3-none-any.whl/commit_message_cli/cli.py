#!/usr/bin/env python3

import argparse
import base64
import json
import logging
import os
import platform
import subprocess
import sys
import time
import zlib
from pathlib import Path
from typing import Any, Dict, Union

import requests

# Constants
DEFAULT_AUTH0_DOMAIN = "auth.production.smoothdev.io"
DEFAULT_AUTH0_CLIENT_ID = "M1eQypHjuCvbzbYBtgI77K2dAGWhhLiq"
DEFAULT_AUTH0_AUDIENCE = "https://auth.production.smoothdev.io/api"
DEFAULT_REDIRECT_URI = "http://app.production.smoothdev.io/auth/callback"
DEFAULT_API_DOMAIN = "rest.production.smoothdev.io"
DEFAULT_CONFIG_FILE = "~/.smoothdevio/config.json"
DEFAULT_FALLBACK_CONFIG_FILE = "~/.smoothdev/config.json"
DEFAULT_SMOOTHDEVIO_DIR = "~/.smoothdevio"
DEFAULT_JWT_FILE = "~/.smoothdevio/jwt"
DEFAULT_JWT_EXPIRY_FILE = "~/.smoothdevio/jwt_expiry"

# Global configuration dictionary
_config: Dict[str, str] = {}

logger = logging.getLogger(__name__)


def configure_logging(debug_flag: bool) -> None:
    """Configure logging level based on debug flag or environment variable."""
    log_level = (
        logging.DEBUG
        if debug_flag or os.getenv("SMOOTHDEV_DEBUG") == "1"
        else logging.INFO
    )
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    logger.debug("Debug logging enabled")


def get_config() -> Dict[str, str]:
    """Get configuration from config file or environment variables."""
    global _config

    if _config:
        return _config

    # Define default values
    _config = {
        "api_domain": DEFAULT_API_DOMAIN,
        "auth0_domain": DEFAULT_AUTH0_DOMAIN,
        "auth0_client_id": DEFAULT_AUTH0_CLIENT_ID,
        "auth0_audience": DEFAULT_AUTH0_AUDIENCE,
        "redirect_uri": DEFAULT_REDIRECT_URI,
        "smoothdevio_dir": DEFAULT_SMOOTHDEVIO_DIR,
        "jwt_file": DEFAULT_JWT_FILE,
        "jwt_expiry_file": DEFAULT_JWT_EXPIRY_FILE,
    }

    # Try to load from primary config file
    config_file = os.path.expanduser(DEFAULT_CONFIG_FILE)
    logger.debug(f"Looking for config file at: {config_file}")
    if Path(config_file).exists():
        logger.debug("Found config file, loading...")
        with open(config_file) as f:
            file_config = json.load(f)
            # Update config with values from file, keeping defaults for missing keys
            _config.update(file_config)
        masked_config = {
            k: "***" if "id" in k.lower() else v for k, v in _config.items()
        }
        logger.debug(f"Loaded config: {json.dumps(masked_config)}")
    else:
        # Try to load from fallback config file
        fallback_config_file = os.path.expanduser(DEFAULT_FALLBACK_CONFIG_FILE)
        logger.debug(f"Looking for fallback config file at: {fallback_config_file}")
        if Path(fallback_config_file).exists():
            logger.debug("Found fallback config file, loading...")
            with open(fallback_config_file) as f:
                file_config = json.load(f)
                # Update config with values from file, keeping defaults for missing keys
                _config.update(file_config)
            masked_config = {
                k: "***" if "id" in k.lower() else v for k, v in _config.items()
            }
            logger.debug(f"Loaded config: {json.dumps(masked_config)}")
        else:
            logger.debug("No config files found, using default values")

    # Load from environment variables, only if they are set
    env_vars = {
        "api_domain": "SMOOTHDEV_API_DOMAIN",
        "auth0_domain": "SMOOTHDEV_AUTH0_DOMAIN",
        "auth0_client_id": "SMOOTHDEV_AUTH0_CLIENT_ID",
        "auth0_audience": "SMOOTHDEV_AUTH0_AUDIENCE",
        "redirect_uri": "SMOOTHDEV_REDIRECT_URI",
        "smoothdevio_dir": "SMOOTHDEV_DIR",
        "jwt_file": "SMOOTHDEV_JWT_FILE",
        "jwt_expiry_file": "SMOOTHDEV_JWT_EXPIRY_FILE",
    }
    for key, env_var in env_vars.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            logger.debug(f"Using environment value for {key}")
            _config[key] = env_value

    # Ensure directory exists
    os.makedirs(os.path.expanduser(_config["smoothdevio_dir"]), exist_ok=True)

    return _config


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate commit message using AI")
    parser.add_argument("-d", "--diff", help="Git diff")
    parser.add_argument("-f", "--file", help="File containing git diff")
    parser.add_argument("-b", "--branch", help="Branch name")
    parser.add_argument("-i", "--issue", help="Issue number")
    parser.add_argument("-c", "--config", help="Config file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def get_diff_input(args: argparse.Namespace) -> str:
    """Get diff input from command line arguments or git."""
    if args.diff:
        return str(args.diff)
    elif args.file:
        with open(str(args.file)) as f:
            content: str = f.read()
            return content
    else:
        return get_diff_input_from_git()


def get_branch_name(args: argparse.Namespace) -> str:
    """Get branch name from command line arguments or git."""
    if args.branch:
        return str(args.branch)
    return get_branch_name_from_git()


def get_issue_key(args: argparse.Namespace) -> Union[str, None]:
    """Get issue key from command line arguments."""
    if args.issue:
        return str(args.issue)
    return None


def validate_diff_input(diff_input: str) -> None:
    """Validate diff input."""
    if not diff_input:
        logger.error("Error: diff input is required.")
        sys.exit(1)


def get_device_code() -> Dict[str, Any]:
    """Get device code from Auth0."""
    config = get_config()
    url = f"https://{config['auth0_domain']}/oauth/device/code"
    data = {
        "client_id": config["auth0_client_id"],
        "scope": "openid profile email",
        "audience": config["auth0_audience"],
    }
    logger.debug(f"Making device code request to: {url}")

    log_data = {k: "***" if k == "client_id" else v for k, v in data.items()}
    logger.debug(f"Request data: {json.dumps(log_data)}")

    try:
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=data,
        )

        if response.status_code != 200:
            logger.error(f"Error response: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            logger.error(f"Request URL: {url}")
            logger.error(f"Request headers: {response.request.headers}")

            # Try to parse the error response
            try:
                error_data = response.json()
                error_type = error_data.get("error", "unknown")
                # Log the error description for better debugging
                error_desc = error_data.get("error_description", "Unknown error")
                logger.error(f"Error details: {error_desc}")

                if error_type == "unauthorized_client" and response.status_code == 403:
                    logger.error(
                        "Client authentication failed. Please check your configuration."
                    )
                    raise Exception(
                        "Authentication failed: Client credentials are "
                        "invalid or expired. Please check your configuration "
                        "or contact support."
                    )
            except ValueError:
                # If we can't parse the JSON, just continue with the standard error
                # handling
                pass

        response.raise_for_status()
        return dict(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise Exception(f"Authentication request failed: {str(e)}") from e


def authenticate_user(device_code_data: Dict[str, Any]) -> None:
    """Authenticate user with Auth0."""
    verification_uri_complete = device_code_data["verification_uri_complete"]
    if platform.system() == "Darwin":
        subprocess.run(["open", verification_uri_complete])
    else:
        subprocess.run(["xdg-open", verification_uri_complete])

    print(f"1. Navigate to: {verification_uri_complete}")
    print(f"2. Enter code: {device_code_data['user_code']}")


def poll_for_token(
    device_code_data: Dict[str, Any], max_poll_time: int = 300
) -> Dict[str, Any]:
    """Poll for the access token with a maximum timeout.

    Args:
        device_code_data: The device code data from get_device_code
        max_poll_time: Maximum time in seconds to poll for the token
            (default: 300 seconds/5 minutes)

    Returns:
        Dict containing the token data

    Raises:
        Exception: If polling times out or other errors occur
    """
    config = get_config()
    token_url = f"https://{config['auth0_domain']}/oauth/token"
    start_time = time.time()
    poll_interval = device_code_data.get(
        "interval", 5
    )  # Default to 5 seconds if not specified

    while True:
        # Check if we've exceeded the maximum polling time
        elapsed_time = time.time() - start_time
        if elapsed_time > max_poll_time:
            msg = f"Authentication timed out after {int(elapsed_time)} seconds"
            logger.error(msg)
            raise Exception(msg)

        try:
            response = requests.post(
                token_url,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code_data["device_code"],
                    "client_id": config["auth0_client_id"],
                },
                timeout=10,  # Add a timeout for the request itself
            )

            # Handle non-JSON responses
            try:
                response_data = dict(response.json())
            except ValueError:
                logger.error(f"Invalid JSON response: {response.text}")
                response_data = {
                    "error": "invalid_response",
                    "error_description": "Invalid response from server",
                }

            if response.status_code == 200:
                return response_data

            # Handle known error codes
            error = response_data.get("error", "")
            error_description = response_data.get("error_description", "Unknown error")

            if error == "authorization_pending":
                # User hasn't completed authentication yet, continue polling
                logger.debug(
                    f"Authorization pending, polling again in {poll_interval} seconds"
                )
                time.sleep(poll_interval)
                continue
            elif error == "slow_down":
                # Auth0 is requesting we slow down our polling
                new_interval = poll_interval + 1
                logger.debug(
                    f"Received slow_down error, increasing interval to "
                    f"{new_interval} seconds"
                )
                poll_interval = new_interval
                time.sleep(poll_interval)
                continue
            elif error == "expired_token" or error == "invalid_grant":
                # Device code has expired
                logger.error("Device code expired. Please try again.")
                raise Exception("Device code expired. Please try again.")
            elif error == "access_denied":
                # User denied the authorization
                logger.error("Authorization denied by user")
                raise Exception("Authorization denied by user")
            else:
                # Other errors
                logger.error(f"Authentication error: {error} - {error_description}")
                raise Exception(error_description)

        except requests.exceptions.RequestException as e:
            # Handle network errors
            logger.error(f"Network error during authentication: {str(e)}")
            time.sleep(poll_interval)
            continue


def get_jwt() -> str:
    """Get JWT token from Auth0.

    This function handles the device authentication flow, including opening a browser
    for user authentication and polling for the token. It includes safeguards against
    timeouts and user cancellation.

    Returns:
        str: The JWT token if authentication is successful

    Raises:
        Exception: If authentication fails, is cancelled, or times out
    """
    max_retries = 3
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            # Try to get device code with retry mechanism
            try:
                device_code_data = get_device_code()
                logger.info(
                    "Device code obtained, launching browser for authentication"
                )
            except Exception as device_error:
                # If we fail to get a device code, retry
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(
                        f"Failed to get device code (attempt {retry_count}/"
                        f"{max_retries}): {str(device_error)}"
                    )
                    logger.info("Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    # If we've exhausted our retries, re-raise the exception
                    logger.error(
                        f"Failed to get device code after {max_retries} attempts"
                    )
                    raise

            # Open browser for user authentication
            try:
                if platform.system() == "Darwin":
                    subprocess.run(
                        ["open", device_code_data["verification_uri_complete"]]
                    )
                else:
                    subprocess.run(
                        ["xdg-open", device_code_data["verification_uri_complete"]]
                    )
                logger.info("Browser launched for authentication")
            except Exception as e:
                logger.warning(f"Failed to open browser automatically: {str(e)}")
                logger.info(
                    f"Please open this URL manually: "
                    f"{device_code_data['verification_uri_complete']}"
                )

            # Poll for token with a maximum timeout
            logger.info("Waiting for authentication to complete...")
            token_data = poll_for_token(device_code_data)
            jwt = str(token_data["access_token"])

            # Save token and expiry
            config = get_config()
            jwt_file = Path(config["jwt_file"]).expanduser()
            jwt_expiry_file = Path(config["jwt_expiry_file"]).expanduser()

            # Ensure the directory exists
            jwt_file.parent.mkdir(parents=True, exist_ok=True)

            jwt_file.write_text(jwt)
            expiry_time = int(time.time()) + token_data["expires_in"]
            jwt_expiry_file.write_text(str(expiry_time))

            logger.info("Authentication completed successfully")
            return jwt

        except KeyboardInterrupt:
            logger.error("Authentication cancelled by user")
            raise Exception("Authentication cancelled by user") from None
        except Exception as e:
            last_error = e
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(
                    f"Authentication attempt {retry_count}/{max_retries} "
                    f"failed: {str(e)}"
                )
                logger.info("Retrying in 2 seconds...")
                time.sleep(2)
            else:
                logger.error(
                    f"Authentication failed after {max_retries} attempts: {str(e)}"
                )
                raise Exception(
                    f"Authentication failed after {max_retries} attempts: {str(e)}"
                ) from e

    # This should never be reached due to the raise in the loop, but just in case
    if last_error:
        raise Exception(f"Authentication failed: {str(last_error)}") from last_error
    else:
        raise Exception("Authentication failed for unknown reasons")


def is_jwt_valid() -> bool:
    """Check if JWT token is valid."""
    config = get_config()
    jwt_file = os.path.expanduser(config["jwt_file"])
    jwt_expiry_file = os.path.expanduser(config["jwt_expiry_file"])

    if not os.path.exists(jwt_file) or not os.path.exists(jwt_expiry_file):
        return False

    with open(jwt_expiry_file) as f:
        expiry = int(f.read().strip())
        return expiry > time.time()


def get_stored_jwt() -> str:
    """Get stored JWT token."""
    config = get_config()
    jwt_file = os.path.expanduser(config["jwt_file"])
    with open(jwt_file) as f:
        return f.read().strip()


def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize the payload to remove sensitive information."""
    sanitized_diff = payload["diff"].replace("169.254.169.254", "[REDACTED]")
    payload["diff"] = sanitized_diff
    return payload


def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the payload for security concerns."""
    if "169.254.169.254" in payload["diff"]:
        raise ValueError("Invalid content in diff input")
    return payload


def encode_payload(payload: Dict[str, Any]) -> str:
    """Encode the payload for transmission using maximum compression."""
    # Use shorter field names
    compact_payload = {
        "d": payload.get("diff", ""),
        "b": payload.get("branch", ""),
        "i": payload.get("issue", ""),
    }
    # Minify JSON by removing whitespace
    payload_json = json.dumps(compact_payload, separators=(",", ":"))
    # Use maximum zlib compression level (9)
    compressed_payload = zlib.compress(payload_json.encode("utf-8"), level=9)
    # Use URL-safe base64 without padding
    encoded_bytes = base64.urlsafe_b64encode(compressed_payload).rstrip(b"=")
    return encoded_bytes.decode("utf-8")


def decode_commit_message(encoded_message: str) -> str:
    """Decode a base64 and zlib compressed commit message."""
    try:
        # Decode base64
        compressed_data = base64.b64decode(encoded_message + "==")
        # Decompress with zlib
        decompressed_data = zlib.decompress(compressed_data)
        # Decode bytes to string
        return decompressed_data.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decode commit message: {str(e)}")
        raise


def get_branch_name_from_git() -> str:
    """Get branch name from git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_diff_input_from_git() -> str:
    """Get diff input from git staged changes."""
    try:
        # First check if there are any staged changes
        check_staged = subprocess.run(
            ["git", "diff", "--staged", "--quiet"],
            capture_output=True,
            text=True,
        )

        # Exit code 1 means there are staged changes
        if check_staged.returncode != 1:
            msg = "No staged changes found. Please stage your changes using git add."
            raise ValueError(msg)

        # Get the actual diff of staged changes
        result = subprocess.run(
            ["git", "diff", "--staged"], capture_output=True, text=True, check=True
        )
        diff_output = result.stdout.strip()
        if not diff_output:
            msg = "No staged changes found. Please stage your changes using git add."
            raise ValueError(msg)
        return diff_output
    except subprocess.CalledProcessError as err:
        raise ValueError("Failed to get git diff") from err


def invalidate_jwt() -> None:
    """Invalidate the stored JWT token by removing the files."""
    config = get_config()
    jwt_file = Path(config["jwt_file"]).expanduser()
    jwt_expiry_file = Path(config["jwt_expiry_file"]).expanduser()

    if jwt_file.exists():
        jwt_file.unlink()
        logger.debug(f"Removed JWT file: {jwt_file}")
    if jwt_expiry_file.exists():
        jwt_expiry_file.unlink()
        logger.debug(f"Removed JWT expiry file: {jwt_expiry_file}")

    logger.info("JWT token invalidated, will re-authenticate")


def main() -> None:
    """Main entry point for the CLI tool."""
    try:
        args = parse_arguments()
        configure_logging(args.debug)

        # Get diff input first to validate it before authentication
        try:
            diff_input = get_diff_input(args)
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)

        validate_diff_input(diff_input)

        # Create payload
        payload = {
            "diff": diff_input,
            "branch": get_branch_name(args),
            "issue": get_issue_key(args),
        }

        # Sanitize, validate and encode payload
        payload = sanitize_payload(payload)
        payload = validate_payload(payload)
        encoded_payload = encode_payload(payload)

        # Configure API request
        config = get_config()
        api_url = f"https://{config['api_domain']}/commit_message_generator"
        request_data = {"payload": encoded_payload}

        # First attempt with existing JWT if valid
        auth_retry = False
        if is_jwt_valid():
            jwt = get_stored_jwt()
        else:
            logger.info("No valid JWT found, initiating authentication flow")
            jwt = get_jwt()

        # Make API request with retry for auth failures
        while True:
            headers = {"Authorization": f"Bearer {jwt}"}

            logger.debug(f"Making API request to: {api_url}")
            log_headers = {
                k: v[:10] + "..." if k.lower() == "authorization" else v
                for k, v in headers.items()
            }
            logger.debug(f"Request headers: {json.dumps(log_headers)}")
            logger.debug(f"Request data: {json.dumps(request_data)}")

            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=request_data,
                )

                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")

                # Handle authentication errors
                if response.status_code == 403 or response.status_code == 401:
                    if auth_retry:
                        logger.error(
                            "Authentication failed after retry. Please try again later."
                        )
                        logger.error("Response body: {}".format(response.text))
                        sys.exit(1)

                    logger.info(
                        f"Authentication error ({response.status_code}), "
                        f"initiating authentication flow"
                    )
                    logger.info(
                        "Your browser will open to complete the authentication process"
                    )
                    invalidate_jwt()

                    try:
                        jwt = get_jwt()
                        auth_retry = True
                        logger.info(
                            "Authentication completed, retrying request with new token"
                        )
                        continue
                    except Exception as auth_error:
                        # Handle authentication errors gracefully
                        if "cancelled by user" in str(auth_error).lower():
                            logger.error("Authentication was cancelled by the user")
                        elif "timed out" in str(auth_error).lower():
                            logger.error(
                                "Authentication timed out. Please try again later"
                            )
                        elif "denied by user" in str(auth_error).lower():
                            logger.error("Authentication was denied by the user")
                        elif "expired" in str(auth_error).lower():
                            logger.error(
                                "Authentication code expired. Please try again"
                            )
                        else:
                            logger.error(f"Authentication failed: {str(auth_error)}")
                        sys.exit(1)

                # Handle other errors
                elif response.status_code != 200:
                    logger.error(
                        f"API request failed with status {response.status_code}"
                    )
                    logger.error(f"Response body: {response.text}")
                    sys.exit(1)

                # Process successful response
                commit_message = response.json().get("commit_message")
                if not commit_message:
                    logger.error("No commit message in response")
                    sys.exit(1)

                decoded_message = decode_commit_message(commit_message)

                # Strip out any markdown formatting before printing
                clean_message = (
                    decoded_message.replace("```plaintext\n", "")
                    .replace("```\n", "")
                    .replace("```", "")
                )
                # Add a newline before printing for better readability
                print(f"\n{clean_message}")
                break

            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {str(e)}")
                sys.exit(1)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
