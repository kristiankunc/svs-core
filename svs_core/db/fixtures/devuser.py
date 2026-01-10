import os
import sys

import django

django.setup()

from django.db import connection

from svs_core.docker.network import DockerNetworkManager
from svs_core.shared.hash import hash_password
from svs_core.users.user import User

devuser = os.getenv("USER", sys.argv[1] if len(sys.argv) > 1 else "")

if not devuser:
    raise ValueError(
        "Devuser not specified. Please set the USER environment variable or pass it as a command line argument."
    )

password_hash = hash_password("12345678").decode("utf-8")

try:
    User.objects.get(name=devuser)
    print(f"Dev user '{devuser}' already exists.")
    sys.exit(0)

except User.DoesNotExist:
    pass

with connection.cursor() as cursor:
    cursor.execute(
        """
        INSERT INTO users (name, password, created_at, updated_at)
        VALUES (%s, %s, NOW(), NOW())
        ON CONFLICT (name) DO NOTHING
        """,
        [devuser, password_hash],
    )

if not DockerNetworkManager.get_network(devuser):
    DockerNetworkManager.create_network(devuser)

print(f"Created dev user '{devuser}' with password '12345678'")
