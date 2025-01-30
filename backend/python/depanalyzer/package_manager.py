import os
import tempfile
import tarfile
from typing import Optional
import requests

class PackageManager:
    """Handles downloading and extracting Python packages from PyPI."""
    
    def __init__(self, packages_dir: str):
        self.packages_dir = packages_dir
        os.makedirs(packages_dir, exist_ok=True)

    def download_and_extract_package(self, package_name: str) -> Optional[str]:
        """Download a package from PyPI and extract it to a local directory.
        Returns the path to the extracted package directory."""
        try:
            # Search for the package on PyPI
            pypi_url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(pypi_url)
            response.raise_for_status()
            
            package_data = response.json()
            latest_version = package_data['info']['version']
            
            # Check if we already have this version downloaded
            package_dir = os.path.join(self.packages_dir, f"{package_name}-{latest_version}")
            if os.path.exists(package_dir):
                print(f"Using cached package: {package_dir}")
                return package_dir
            
            # Find the source distribution URL
            sdist_url = None
            for url in package_data['urls']:
                if url['packagetype'] == 'sdist':
                    sdist_url = url['url']
                    break
            
            if not sdist_url:
                print(f"No source distribution found for {package_name}")
                return None
            
            print(f"Downloading {package_name} from {sdist_url}")
            
            # Download and extract the package
            response = requests.get(sdist_url)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix='.tar.gz') as temp_file:
                temp_file.write(response.content)
                temp_file.flush()
                
                print(f"Extracting to {package_dir}")
                with tarfile.open(temp_file.name, 'r:gz') as tar:
                    def is_within_limits(members):
                        for member in members:
                            if member.size < 10000000:  # Skip files larger than 10MB
                                yield member
                    tar.extractall(path=self.packages_dir, members=is_within_limits(tar))
            
            print(f"Package dir: {package_dir}")
            return package_dir
            
        except Exception as e:
            print(f"Error downloading package {package_name}: {e}")
            return None
