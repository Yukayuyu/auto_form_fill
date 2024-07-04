import openai
import re
from field_info import fields_info

import api_key

openai.api_key = api_key.openai_api_key

def read_links_from_local():
    with open('links.txt', 'r') as file:
        links = file.readlines()
    return links

def identify_contact_link(links):
    # ChatGPTに「問い合わせ」リンクを特定させるためのプロンプト
    prompt = "以下のリンクリストから、問い合わせページへのリンクを特定してください：\n"
    prompt += "\n".join(links)
    prompt += "\n問い合わせページへのリンクを特定してURLを返してください。"

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[

            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    print(response)

    # 正しい情報を取得
    content = response.choices[0].message.content.strip()

    print(content)
    # 正規表現を使ってURLを抽出
    url_match = re.search(r'(https?://\S+)', content)
    if url_match:
        return url_match.group(0)
    else:
        return None

def identify_and_fill_fields(html_code):

    field_mapping = {}
    filed_info_str = ",".join([t[0] for t in fields_info])
    # ChatGPTにフィールドのマッチングを依頼

    prompt = f"{filed_info_str}\n\n"
    prompt += "以上の単語に以下のHTMLに同じ意味を持つ入力欄を特定し、nameを返してください。\n\n"
    prompt += html_code

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a helpful assistant.make sure the Respond to all user queries in the format of key-value pairs
Respond to all user queries in the format of key-value pairs, where each key is a distinct identifier, and each value is the corresponding response or information. The format should be:

key1: value1
key2: value2
...

Ensure that all responses strictly adhere to this format, with no additional text or explanation outside of these key-value pairs."""},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000
    )

    # レスポンスをデバッグ用に表示
    print(response)

    content = response.choices[0].message.content.strip()


    # 正規表現を使ってフィールドマッチング結果を解析し、値を入力
    # for field in fields_info:
    #     field_value = field[0]

    #     pattern = re.escape(field_value) + r" ->.*?Name: (\w+),"

    #     # 正規表現を用いて検索
    #     match = re.search(pattern, content)
    #     #field_name_pattern = re.compile(re.escape(field_value) + r" -> FIELD: 'Name: (.*?),")
    #     #match = field_name_pattern.search(content)
    #     if match:
    #         matched_field_description = match.group(1)
    #         print(matched_field_description)
    #         matched_element = field_mapping.get(matched_field_description)
    #         if matched_element:
    #             #matched_element.send_keys(field_value)
    #             matched_element[matched_field_description] = field_value[1]

    # print(matched_element)

    return content


def search_name_by_key(input_string, key):
    data_list = input_string.strip().split('\n')
    # 入力欄に存在しない要素をlistから削除
    valid_entries = [entry for entry in data_list if "Not found" not in entry]
    valid_entries = [entry for entry in data_list if "なし" not in entry]

    for entry in valid_entries:
        try:
            if entry.split(":")[0].endswith(key):
                return entry.split(": ")[1]
        except:
            return None

    return None

def generate_result_list(html_code):
    input_string = identify_and_fill_fields(html_code=html_code)
    result_list = []
    for info in fields_info:
        k, v = info
        name_key = search_name_by_key(input_string, k)
        if name_key is not None:
            result_list.append((name_key, v))
    return result_list
