"""Read-only production HTTP checks. Never submits forms or follows checkout links."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
URLS = ['https://interviewsarthi.com/' + p for p in (
    '', 'robots.txt', 'sitemap.xml', 'about.html', 'help.html',
    'guides/', 'ai-interview-assistant-india.html',
    'best-ai-interview-assistant-india.html', 'hinglish-interview-help.html',
    'thanks.html', '404.html')]


def check(url):
    result = {'url':url}
    try:
        with urlopen(Request(url, headers={'User-Agent':'InterviewSarthi-SEO-Review/1.0'}), timeout=15) as response:
            body = response.read(2_000_000).decode('utf-8', errors='replace')
            result.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type'),
                          x_robots_tag=response.headers.get('X-Robots-Tag'))
            if url.endswith(('robots.txt','sitemap.xml')):
                result['body']=body
    except HTTPError as exc:
        result['status']=exc.code
    except Exception as exc:
        result['error']=str(exc)
    return result


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(check, URLS))
    output={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'results':results,
            'scope':'Pre-deployment HTTP observations; not a verified Google/AI crawler test.'}
    (ROOT/'research/live-http-baseline.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    for result in results:
        print(json.dumps({key:value for key,value in result.items() if key!='body'}))
