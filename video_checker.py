import requests
from xml.etree import ElementTree
import csv
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

def load_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        content = response.content.decode('utf-8').strip()
        if not content:
            raise ValueError("Empty sitemap content")
        return ElementTree.fromstring(content)
    except requests.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        return None
    except ElementTree.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

def get_video_sitemaps(root):
    video_sitemaps = []
    for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
        if 'videos' in sitemap.text.lower():
            video_sitemaps.append(sitemap.text)
    return video_sitemaps

def main():
    # Configure these variables
    sitemap_url = "sitemap_url"
    beta_domain = "beta_url"
    
    print("Loading main sitemap...")
    root = load_sitemap(sitemap_url)
    
    if root is None:
        print("Failed to load main sitemap. Exiting...")
        return
    
    # Get all video sitemaps
    video_sitemaps = get_video_sitemaps(root)
    print(f"Found {len(video_sitemaps)} video sitemaps")
    
    # Process just the first video sitemap and get one video
    if video_sitemaps:
        print(f"Processing video sitemap: {video_sitemaps[0]}")
        video_sitemap_root = load_sitemap(video_sitemaps[0])
        if video_sitemap_root is not None:
            for url in video_sitemap_root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                video_loc = url.find('.//{http://www.google.com/schemas/sitemap-video/1.1}content_loc')
                if video_loc is not None:
                    # Get just one video URL and break
                    video_url = video_loc.text
                    print(f"Testing single video URL: {video_url}")
                    result = check_video_url(video_url, beta_domain)
                    
                    # Print the result
                    print("\nTest Result:")
                    print(f"Original URL: {result['original_url']}")
                    print(f"Beta URL: {result['beta_url']}")
                    print(f"Status: {result['status']}")
                    print(f"Working: {result['working']}")
                    return
    
    print("No videos found in the sitemap.")
    # Process each video sitemap
    all_video_urls = []
    for video_sitemap_url in video_sitemaps:
        print(f"Processing video sitemap: {video_sitemap_url}")
        video_sitemap_root = load_sitemap(video_sitemap_url)
        if video_sitemap_root is not None:
            for url in video_sitemap_root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                video_loc = url.find('.//{http://www.google.com/schemas/sitemap-video/1.1}content_loc')
                if video_loc is not None:
                    all_video_urls.append(video_loc.text)
    
    print(f"Found {len(all_video_urls)} total videos. Checking availability...")
    
    # Check videos in parallel
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_video_url, url, beta_domain) for url in video_urls]
        for future in futures:
            results.append(future.result())
    
    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'video_check_report_{timestamp}.csv'
    
    with open(report_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['original_url', 'beta_url', 'status', 'working'])
        writer.writeheader()
        writer.writerows(results)
    
    # Print summary
    working_count = sum(1 for r in results if r['working'])
    print(f"\nResults:")
    print(f"Total videos checked: {len(results)}")
    print(f"Working videos: {working_count}")
    print(f"Non-working videos: {len(results) - working_count}")
    print(f"Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main()