Posting Status
==============

Currently minimal_activitypub only implements standard status posting (polls and direct messages / DMs
are not currently implemented).


Posting text only status
------------------------

The sample code below shows a very simple text only status being posted.

.. code-block:: python
   :linenos:

   from minimal_activitypub.client_2_server import ActivityPub
   from minimal_activitypub import Status

   async def post_status(instance_api: ActivityPub, status: str) -> Status:

      posted_status = await instance_api.post_status(status=status)


Posting status that includes picture
------------------------------------

The sample code below shows how to post a status with images attached. Basically the images/media needs
to be posted first and the media id(s) need to be included when posting the status itself.

.. code-block:: python
   :linenos:

   import aiofiles
   import magic
   from minimal_activitypub.client_2_server import ActivityPub
   from minimal_activitypub import Status

   async def post_status(instance_api: ActivityPub, status: str, image_path: str) -> Dict[str, Any]:

      # First determine mime-type
      mime_type = magic.from_file(image_path, mime=True)

      # Post media
      async with aiofiles.open(image_path, "rb") as image_file:
         posted_media = await instance_api.post_media(file=image_file, mime_type=mime_type)

      # Determine media id to include when posting status
      media_id = posted_media["id"]

      # Post actual status and include image
      posted_status = await instance_api.post_status(status=status, media_ids=[media_id])



Method Signatures
-----------------

Following are the method signatures used in the above examples.

.. autoclass:: minimal_activitypub.client_2_server.ActivityPub
   :members: post_media, post_status
   :noindex:
