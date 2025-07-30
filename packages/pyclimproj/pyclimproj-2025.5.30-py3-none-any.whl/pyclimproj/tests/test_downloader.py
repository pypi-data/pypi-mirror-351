import os
import shutil
import random
from urllib.parse import urljoin
from pyclimproj.downloader import Downloader

def test_collect_download_links_only():
    test_dir = "test_output"
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)

    d = Downloader(out_dir=test_dir, verbose=False)

    # Use real top-level directory listing
    top_level_dirs = d._list_subdirs(d.root_url)
    sampled_dirs = random.sample(top_level_dirs, min(20, len(top_level_dirs)))

    collected_links = []

    for gcm_ssp in sampled_dirs:
        gcm_ssp_url = urljoin(d.root_url + "/", gcm_ssp)
        var_dirs = d._list_subdirs(gcm_ssp_url)

        for var in var_dirs:
            if "prcp" not in var.lower():
                continue
            var_url = urljoin(gcm_ssp_url + "/", var)
            file_list = d._list_subdirs(var_url)

            # Filter files by temporal resolution
            files = [f for f in file_list if f.endswith(".nc") and "yr_1980_2019" in f]

            for file in files:
                full_url = urljoin(var_url + "/", file)
                collected_links.append(full_url)
                if len(collected_links) >= 10:
                    break
            if len(collected_links) >= 10:
                break
        if len(collected_links) >= 10:
            break

    # Save to file inside test_output/
    output_file = os.path.join(test_dir, "download_links_only.txt")
    with open(output_file, "w") as f:
        for link in collected_links:
            f.write(link + "\n")

    assert len(collected_links) > 0, "No links collected"
    print(f"Collected {len(collected_links)} links. Saved to '{output_file}'")
