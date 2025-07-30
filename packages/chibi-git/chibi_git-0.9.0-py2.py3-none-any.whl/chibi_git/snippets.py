def get_base_name_from_git_url( url ):
    return url.rsplit( '.', 1 )[0].rsplit( '/', 1 )[ 1 ]


def remove_start_asterisk( branch ):
    if branch.startswith( '*' ):
        branch = branch[2:]
    return branch
