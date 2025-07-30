import os
import sys
import argparse
import requests
import datetime
from dotenv import load_dotenv
load_dotenv()

def grok_search(query:str):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
    }
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (f"あなたはWebサイトの検索を行います。"
                            f"間違いが無いように気を付けます。"
                            f"今の日時は {datetime.datetime.now()} です。")
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "search_parameters": {
            "mode": "auto"
        },
        "model": "grok-3-latest"
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    result_content = result["choices"][0]["message"]["content"]
    return result_content


def main():
    parser = argparse.ArgumentParser(description='GrokでWeb検索を実行します')
    parser.add_argument('query', help='検索クエリ')
    parser.add_argument('-v', '--verbose', action='store_true', help='詳細な出力を表示')
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"検索中: {args.query}")
        
        result = grok_search(args.query)
        print(result)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
