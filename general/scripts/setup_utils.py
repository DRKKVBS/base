import os
import shutil
import logging


def add_desktop_app(file_path: str, user: str, visible_apps: list):
    path = get_mount_point()

    try:
        uid = get_uid(user)
        gid = get_gid(user)

    except ValueError as e:
        logging.error(e)
        return

    applications_path = os.path.normpath(
        "%s/home/%s/.local/share/applications/" % (path, user))

    if not os.path.exists(applications_path):
        mkdirs_as_user(dir=path, user=user)

    make_mutable(os.path.normpath(
        "/home/%s/.local/share/applications/" % user))

    app = os.path.split(file_path)[1]

    if os.path.exists(os.path.normpath(f'{applications_path}/{app}')):
        print_color.print_warning(
            "The file %s is already added to the %s" % (app, user))
        make_immutable(os.path.normpath(
            "/home/%s/.local/share/applications/" % user))
        return

    shutil.copyfile(
        file_path, os.path.normpath(f'{applications_path}/{app}'))
    print(os.path.normpath(f'{applications_path}/{app}'), uid, gid)
    shutil.chown(os.path.normpath(f'{applications_path}/{app}'), uid, gid)

    if app in visible_apps:
        show_desktop_app(app, user)
    else:
        hide_desktop_app(app, user)

    make_immutable(os.path.normpath(
        "/home/%s/.local/share/applications/" % user))
    make_immutable(os.path.normpath(
        f"/home/{user}/.local/share/applications/{app}"))


def hide_desktop_app(app: str, user: str):
    '''Hide a desktop app from user so he cannot access via the acitvities screen.'''

    path = get_mount_point()

    if not os.path.exists(os.path.normpath("%s/home/%s/.local/share/applications/%s" % (path, user, app))):
        print_color.print_info(
            "The app %s is not accessible to %s" % (app, user))
        return
    make_mutable(os.path.normpath(
        "/home/%s/.local/share/applications/%s" % (user, app)))
    with open(os.path.normpath(
            "%s/home/%s/.local/share/applications/%s" % (path, user, app)), "r+") as f:
        content = f.read()

        if "NoDisplay=true" in content:
            print_color.print_info(
                "%s is already hidden from %s" % (app, user))

        elif "NoDisplay=false" in content:
            content = content.replace(
                "NoDisplay=false", "NoDisplay=true")

        elif "NoDisplay" not in content:
            content = content.replace(
                "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true")

        f.seek(0)
        f.truncate()
        f.write(content)

    make_immutable(os.path.normpath(
        "/home/%s/.local/share/applications/%s" % (user, app)))


def show_desktop_app(app: str, user: str):
    '''Show a desktop app to user so he can access via the acitvities screen.'''
    path = get_mount_point()

    if not os.path.exists(os.path.normpath(
            "%s/home/%s/.local/share/applications/%s" % (path, user, app))):
        print_color.print_info(
            "The app %s is not accessible to %s" % (app, user))
        return
    make_mutable(os.path.normpath(
        "/home/%s/.local/share/applications/%s" % (user, app)))
    with open(os.path.normpath(
            "%s/home/%s/.local/share/applications/%s" % (path, user, app)), "r+") as f:
        content = f.read()

        if "NoDisplay=false" in content:
            print_color.print_info(
                "%s is already visible for %s" % (app, user))

        elif "NoDisplay=true" in content:
            content = content.replace(
                "NoDisplay=true", "NoDisplay=false")

        elif "NoDisplay" not in content:
            content = content.replace(
                "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=false")

        f.seek(0)
        f.truncate()
        f.write(content)

    make_immutable(os.path.normpath(
        "/home/%s/.local/share/applications/%s" % (user, app)))


if __name__ == "__main__":
    root_dir = os.path.realpath(os.path.dirname(__file__)).split("scripts")[0]
