#!/usr/bin/env uv run

import sys

import slugkit

logins = slugkit.SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="ik-dEHLbeWo5MXfHX9LGBsksCjZkiBizL+ySG2lNRDZhWdtuBIkN04y4FIpMbUiheCOG5PI2MCuZMRgRm1UQpB14w==",
)

names = slugkit.SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="ik-O613ug0Snl52VP9jjM4vmOTfVI+Rbn2JIif+5v/msrD6xOTM8yMoycUztBWl1SZqhKjFVc3KAV0bKzKStzc8ww==",
)

passwords = slugkit.SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="ik-xChoMQGzL8nFlRzbzNajqIJz/yktPeHflNH9e1Cobq0Obv9qZZvX2lKA6pZYvkck69DUlj6K8RkZnGYJ5dbWjA==",
)

if __name__ == "__main__":
    num_names = 1
    if len(sys.argv) > 1:
        num_names = int(sys.argv[1])
    login_gen = logins.generator.with_limit(num_names)
    name_gen = names.generator.with_limit(num_names)
    pass_gen = passwords.generator.with_limit(num_names)
    for login, name, password in zip(login_gen, name_gen, pass_gen):
        print(f"{login:15s}\t{name:15s}\t{password}")
