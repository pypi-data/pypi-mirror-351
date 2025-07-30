import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

class Downloader:
    def __init__(self, root_url="https://hydrosource2.ornl.gov/files/SWA9505V3/", out_dir="downloads", verbose=True):
        self.root_url = root_url.rstrip("/")
        self.out_dir = out_dir
        self.verbose = verbose
        os.makedirs(self.out_dir, exist_ok=True)

    def _list_subdirs(self, url):
        if self.verbose:
            print(f"Scanning: {url}")
        try:
            r = requests.get(url)
            r.raise_for_status()
        except Exception as e:
            print(f"Failed to access {url}: {e}")
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        return [node.get('href') for node in soup.find_all('a') if node.get('href') not in (None, '../')]

    def download_bulk(self, gcms, scenarios, variables, temporal_res=None, download_limit=None):
        top_dirs = self._list_subdirs(self.root_url)
        matched_dirs = []

        for folder in top_dirs:
            folder_clean = folder.strip('/')
            if not any(gcm in folder_clean for gcm in gcms):
                continue
            if not any(ssp in folder_clean for ssp in scenarios):
                continue
            matched_dirs.append(folder_clean)

        if self.verbose:
            print("\nMatched folders:")
            for m in matched_dirs:
                print(f"   ➤ {m}")

        download_count = 0

        for gcm_ssp in tqdm(matched_dirs, desc="🔍 GCM–SSP Folders"):
            gcm_ssp_url = urljoin(self.root_url + "/", gcm_ssp + "/")
            var_dirs = self._list_subdirs(gcm_ssp_url)

            if self.verbose:
                print(f"\nExploring variables in {gcm_ssp}")

            for var in var_dirs:
                var_name = var.strip('/').lower()
                if var_name not in variables:
                    continue

                var_url = urljoin(gcm_ssp_url, var)
                local_path = os.path.join(self.out_dir, gcm_ssp, var_name)

                # Identify relevant .nc files
                nc_files = [
                    f for f in self._list_subdirs(var_url)
                    if f.endswith('.nc') and (temporal_res is None or temporal_res in f)
                ]

                for item in tqdm(nc_files, desc=f"Downloading {gcm_ssp}/{var_name}", leave=False):
                    full_url = urljoin(var_url + "/", item)
                    local_file_path = os.path.join(local_path, os.path.basename(item))

                    if os.path.exists(local_file_path):
                        continue

                    try:
                        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                        with requests.get(full_url, stream=True) as r:
                            r.raise_for_status()
                            with open(local_file_path, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        download_count += 1
                        if download_limit and download_count >= download_limit:
                            print(f"\nDownload limit of {download_limit} reached.")
                            return
                    except Exception as e:
                        print(f"Failed to download {full_url}: {e}")
