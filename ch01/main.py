import requests
import os
from os.path import basename
import json
import sys
import tempfile
from google.cloud import storage


PER_PAGE = 100
GS_BUCKET_NAME = os.environ["GS_BUCKET_NAME"]
TOKEN = os.environ["GIT_TOKEN"]
headers = {"Authorization": "token {}".format(TOKEN),
           "Accept": "application/vnd.github.v3+json"
           }
LINK_HEADER = "Link"

class GsUpload():
    """ For dev purpose, env variable GOOGLE_APPLICATION_CREDENTIALS is used
    """

    @staticmethod
    def upload_blob(bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket.
        Src from:
        https://github.com/GoogleCloudPlatform/python-docs-samples/blob\
        /89e67bcb655ed6d120dee46d2d40d866f7c72a59/storage/cloud-client/storage_upload_file.py
        """
        # bucket_name = "your-bucket-name"
        # source_file_name = "local/path/to/file"
        # destination_blob_name = "storage-object-name"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)
        print("File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
                                               )
              )


def do_the_issues(user_id, repo_id):
    """ Fetch issues for the github repo (user_id, repo_id) and dump it to
    google cloud storage bucket=GS_BUCKET_NAME
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "{}_{}_issues.txt".format(repo_id, user_id))
        issues_initial_url = get_initial_url_issues(user_id, repo_id)
        resp_obj = requests.get(issues_initial_url, headers=headers)
        # prase the initial request. for Issue
        all_issues = json.loads(resp_obj.text)
        with open(path, "w") as out_stream:
            for an_issue in all_issues:
                print(an_issue, file=out_stream)
        print("the len of resp is {}".format(len(all_issues)))
        LINK_HEADER = "Link"
        next_url = None
        if LINK_HEADER in resp_obj.headers:
            # parse next page (if present)
            next_url = parse_next_url(resp_obj.headers[LINK_HEADER])
        # subsequent page
        while next_url:
            resp_obj = requests.get(next_url, headers=headers)
            all_issues = json.loads(resp_obj.text)
            with open(path, "a") as out_stream:
                for an_issue in all_issues:
                    print(an_issue, file=out_stream)
            if LINK_HEADER in resp_obj.headers:
                next_url = parse_next_url(resp_obj.headers[LINK_HEADER])
                print(next_url)
            else:
                next_url = None
        GsUpload.upload_blob(GS_BUCKET_NAME, path, basename(path))
        print("the issues path is " + str(path))


def do_the_pulls(user_id, repo_id):
    """ Fetch pulls for the github repo (user_id, repo_id) and dump it to
    google cloud storage bucket=GS_BUCKET_NAME
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = os.path.join(tmp_dir, "{}_{}_pulls.txt".format(repo_id, user_id)
                            )

        # the first request for pull
        the_url = get_initial_url_pulls(user_id, repo_id)
        resp_obj = requests.get(the_url, headers=headers)
        pull_requests = json.loads(resp_obj.text)
        with open(path, "w") as out_stream:
            for a_pull_request in pull_requests:
                print(a_pull_request, file=out_stream)

        # prase the initial request.
        rsp_json = json.loads(resp_obj.text)
        print("the len of resp is {}".format(len(rsp_json)))
        next_url = None
        if LINK_HEADER in resp_obj.headers:
            next_url = parse_next_url(resp_obj.headers[LINK_HEADER])

        # subsequent requests for pull
        while next_url:
            resp_obj = requests.get(next_url, headers=headers)
            pull_requests = json.loads(resp_obj.text)
            with open(path, "a") as out_stream:
                for a_pull_request in pull_requests:
                    print(a_pull_request, file=out_stream)
            if LINK_HEADER in resp_obj.headers:
                next_url = parse_next_url(resp_obj.headers[LINK_HEADER])
                print(next_url)
            else:
                next_url = None
        GsUpload.upload_blob(GS_BUCKET_NAME, path, basename(path))


def parse_next_url(link_str):
    """ Given the Link header string;
    see: https://developer.github.com/v3/#pagination
    parse the next url
    """
    links_arr = link_str.split(",")
    for links in links_arr:
        a_url, direction = links.split(';')
        if "next" in direction:
            a_url = a_url.replace('<', '').replace('>', '')
            return a_url
    return None


def get_initial_url_pulls(user_id, repo_id):
    """ Pull Requests
    """
    the_url = "https://api.github.com/repos/{}/{}/pulls?page=1&per_page={}"\
              .format(user_id, repo_id, PER_PAGE)
    return the_url


def get_initial_url_issues(user_id, repo_id):
    """ Issues
    """
    the_url = "https://api.github.com/repos/{}/{}/issues?page=1&per_page={}"\
              .format(user_id, repo_id, PER_PAGE)
    return the_url


def fetch_and_dump(user_id, repo_id):
    do_the_issues(user_id, repo_id)
    do_the_pulls(user_id, repo_id)


def do_the_query(request):
    """ The entry point into the function
    """

    # TODO Check if params are there..
    # TODO return error code if not present
    user_id = request.args.get("user_id")
    repo_id = request.args.get("repo_id")
    print(user_id, repo_id)
    fetch_and_dump(user_id, repo_id)
    return (str([user_id, repo_id]), 200, {"Output": "Works"})


def get_query():
    """ The graph QL Query
    """
    query = """{
   repository(name: "flux", owner: "fluxcd") {
    forkCount
    issues {
      totalCount
    }
    pullRequests {
      totalCount
    }
    releases {
      totalCount
    }
    stargazers {
      totalCount
    }
    watchers {
      totalCount
    }
  }
}
   """
    return query

