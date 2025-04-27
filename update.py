# -*- coding: utf-8 -*-

from __future__ import annotations
from fake_useragent import UserAgent
import requests
import time
import base64
import json

SLEEP_TIME = 1.5
PAGE_SIZE    = 50

def find_all_profs(school_legacy_id: int = 4928) -> list:
    """
    Request list of all prof data from a school.
    default id(utm): 4928
    """
    # encode schoolLegacyId as base64 as required by GraphQL
    school_encoded = base64.b64encode(f"School-{school_legacy_id}".encode()).decode()

    url = "https://www.ratemyprofessors.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": UserAgent().random,
        "Origin": "https://www.ratemyprofessors.com",
        "Referer": f"https://www.ratemyprofessors.com/search/professors/{school_legacy_id}?q=*",
        "Authorization": "Basic dGVzdDp0ZXN0",
        # ↓ your cookie here
        "Cookie": ""
    }

    # check if all can be decoded by latin-1
    for k, v in headers.items():
        try:
            v.encode("latin-1")
        except UnicodeEncodeError:
            raise RuntimeError(f"Header {k!r} has string that cannot be decoded")

    # network packet capture tools show rmp uses graphql
    query = """
    query NewSearchTeachersQuery(
      $query: TeacherSearchQuery!,
      $first: Int!,
      $after: String
    ) {
      newSearch {
        teachers(query: $query, first: $first, after: $after) {
          edges {
            cursor
            node {
              id
              firstName
              lastName
              department
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """

    all_teachers = []
    end_cursor   = None
    has_next     = True

    while has_next:
        variables = {
            "query": {
                "text": "",
                "schoolID": school_encoded,
                "fallback": False
            },
            "first": PAGE_SIZE,
            "after": end_cursor
        }

        resp = requests.post(
            url, headers=headers,
            json={"query": query, "variables": variables}
        )
        data = resp.json()
        resp.close()

        block = data["data"]["newSearch"]["teachers"]

        for edge in block["edges"]:
            n = edge["node"]
            all_teachers.append({
                "id":         n["id"],
                "name":       f"{n['firstName']} {n['lastName']}",
                "department": n["department"]
            })

        # next page
        page_info    = block["pageInfo"]
        has_next     = page_info["hasNextPage"]
        end_cursor   = page_info["endCursor"]

        print(f"Done %s profs" % len(all_teachers))
        time.sleep(SLEEP_TIME)

    return all_teachers


def request_load_more_comments(id: str) -> list:
    """
    Return list of all comments under a prof.
    id: num(str) to represent a prof
    """

    url = "https://www.ratemyprofessors.com/graphql"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic dGVzdDp0ZXN0",
        "User-Agent": UserAgent().random,
        "Referer": "https://www.ratemyprofessors.com/professor",
        "Origin": "https://www.ratemyprofessors.com",
        # ↓ your cookie here
        "Cookie": ""
    }

    query = """
    query RatingsListQuery($id: ID!, $first: Int!, $after: String) {
      node(id: $id) {
        ... on Teacher {
          ratings(first: $first, after: $after) {
            pageInfo {
              hasNextPage
              endCursor
            }
            edges {
              node {
                comment
                difficultyRating
                clarityRating
                helpfulRating
                wouldTakeAgain
                grade
                class
                date
                ratingTags
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "id": id,  # Prof id
        "first": 20,
        "after": None
    }

    comments = []

    while True:
        resp = requests.post(url,
                             headers=headers,
                             json={"query": query, "variables": variables})
        data = resp.json()
        resp.close()
        # print(data)
        ratings = data['data']['node']['ratings']
        for edge in ratings['edges']:
            comments.append(edge['node'])
        if not ratings['pageInfo']['hasNextPage']:
            break
        variables['after'] = ratings['pageInfo']['endCursor']
        time.sleep(SLEEP_TIME)  # make sure not be banned

    print(f"Got {len(comments)} comments")
    return comments


def save_all_professor_data_to_json(filename = "data/all_prof_data.json"):
    all_profs = find_all_profs()  # get all profs
    all_data = []  # final data

    for i, prof in enumerate(all_profs):
        print(f"processing {prof['name']} ({i+1}/{len(all_profs)})")

        try:
            comments = request_load_more_comments(prof['id'])  # comments
        except Exception as e:
            print(f"failed to get comment：{prof['name']}，error：{e}")
            comments = []

        prof_data = {
            "id": prof["id"],
            "name": prof["name"],
            "department": prof["department"],
            "comments": comments
        }

        all_data.append(prof_data)

        # save the data when a prof is done processing
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2)

        time.sleep(SLEEP_TIME)

    print(f"all done to {filename}")


if __name__ == '__main__':
    import shutil
    import os

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    source_file = os.path.join(BASE_DIR, 'data', 'all_prof_data.json')
    backup_dir = os.path.join(BASE_DIR, 'data', 'data_copy')
    backup_file = os.path.join(backup_dir, 'all_prof_data.json')
    shutil.copy(source_file, backup_file)

    save_all_professor_data_to_json()
