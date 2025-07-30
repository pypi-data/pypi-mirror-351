Authentication Flows
====================

To authenticate you will need an access token from the fediverse instance you are connecting to.
Minimal-activitypub supports two different ways of generating access tokens. One requires that
the `Username and password`_ is supplied, the other generates an `Authorization URL`_ that a user needs to
visit to generate an authorization code that then needs to be supplied to minimal-activitypub to
ultimately generate an access token.

.. _Username and Password:

Username and password
---------------------

The sample code below shows the steps needed to generate an access token with having a user visit
a URL and then input the authorization code provided on that URL to ultimately generate an access token.

.. code-block:: python
   :linenos:

   from minimal_activitypub.client_2_server import ActivityPub
   from httpx import AsyncClient

   async def get_access_token(mastodon_domain, user_name, password):

      async with AsyncClient(http2=True) as client:
         # Create app
         client_id, client_secret = await ActivityPub.create_app(
            instance_url=mastodon_domain,
            client=client,
         )


         # Get access token
         access_token = await ActivityPub.get_auth_token(
            instance_url=instance,
            username=user_name,
            password=password,
            client=client,
         )

.. _Authorization URL:

Authorization URL
-----------------

The sample code below shows the steps needed to generate an access token with having a user visit
a URL and then input the authorization code provided on that URL to ultimately generate an access token.

.. code-block:: python
   :linenos:

   from minimal_activitypub.client_2_server import ActivityPub
   from httpx import AsyncClient

   async def get_access_token(mastodon_domain):

      async with AsyncClient(http2=True) as client:
         # Create app
         client_id, client_secret = await ActivityPub.create_app(
            instance_url=mastodon_domain,
            client=client,
         )

         # Get Authorization Code / URL
         authorization_request_url = (
            await ActivityPub.generate_authorization_url(
                instance_url=mastodon_domain,
                client_id=client_id,
                user_agent=USER_AGENT,
            )
         )
         print(
            f"Please go to the following URL and follow the instructions:\n"
            f"{authorization_request_url}"
         )
         authorization_code = input("[...] Please enter the authorization code:")

         # Validate authorization code and get access token
         access_token = await ActivityPub.validate_authorization_code(
            client=client,
            instance_url=mastodon_domain,
            authorization_code=authorization_code,
            client_id=client_id,
            client_secret=client_secret,
         )

         # Verify access token works
         mastodon = ActivityPub(
            instance=mastodon_domain,
            access_token=access_token,
            client=client,
         )
         await mastodon.determine_instance_type()
         user_info = await mastodon.verify_credentials()

Method Signatures
-----------------

Following are the method signatures used in the above examples.

.. autoclass:: minimal_activitypub.client_2_server.ActivityPub
   :members: create_app, get_auth_token, generate_authorization_url, validate_authorization_code,
             determine_instance_type, verify_credentials
   :noindex:
