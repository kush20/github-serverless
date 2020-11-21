

curl -H "Authorization: token ${GIT_TOKEN}"  https://api.github.com/graphql -X POST  -d '
{"query":"{ repository(name: \"flux\", owner: \"fluxcd\") {    id  }}","variables":{}}'


curl -H "Authorization: token ${GIT_TOKEN}"  https://api.github.com/graphql -X POST  -d '
{"query":"{ repository(name: \"flux\", owner: \"fluxcd\") {forkCount    issues {      totalCount    }    pullRequests {      totalCount    }    releases {      totalCount    }    stargazers {      totalCount    }    watchers {      totalCount    } }}","variables":{}}'



# Add invocations of the GitHub V3 API to retrieve the fields below. 
# Some of these are paginated and will require multiple invocations. Each invocation will return an array of objects; print each object to the console.
# Stats/contributors
# Pull requests
# Issues

curl -H "Authorization: token ${GIT_TOKEN}"  https://api.github.com/repos/fluxcd/flux/pull 
curl -H "Accept: application/vnd.github.v3+json"  \
    -H "Authorization: token ${GIT_TOKEN}"  \
    https://api.github.com/repos/fluxcd/flux
curl  -i \
    -H "Accept: application/vnd.github.v3+json"  \
    -H "Authorization: token ${GIT_TOKEN}"  \
    'https://api.github.com/repos/fluxcd/flux/pulls?page=1&per_page=100'


# Link: <https://api.github.com/repositories/62799996/pulls?page=2>; rel="next", <https://api.github.com/repositories/62799996/pulls?page=2>; rel="last"

# issues..
curl  -I  -H "Accept: application/vnd.github.v3+json"  -H "Authorization: token ${GIT_TOKEN}"  https://api.github.com/repos/fluxcd/flux/issues


