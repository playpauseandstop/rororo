GITHUB_USERNAME = "github-user"
GITHUB_PERSONAL_TOKEN = "github-user-personal-token"
GITHUB_REPOSITORY = "github-repo"

GITHUB_REPOSITORIES = {
    GITHUB_USERNAME: {
        GITHUB_REPOSITORY: {
            "uid": "ac711a94-adfa-43ff-8f11-195d78c6f57d",
            "owner": GITHUB_USERNAME,
            "name": GITHUB_REPOSITORY,
            "jobs": ["test", "deploy"],
            "status": "ready",
        }
    }
}

ENVIRONMENT_VARS = {
    GITHUB_USERNAME: {
        "HOME": f"/home/{GITHUB_USERNAME}",
        "TIME_ZONE": "Europe/Kiev",
    },
    f"{GITHUB_USERNAME}/{GITHUB_REPOSITORY}": {"LOCALE": "uk_UA.UTF-8"},
}
