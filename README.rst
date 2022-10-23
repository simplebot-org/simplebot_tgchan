Telegram Channels Bridge
========================

.. image:: https://img.shields.io/pypi/v/simplebot_tgchan.svg
   :target: https://pypi.org/project/simplebot_tgchan

.. image:: https://img.shields.io/pypi/pyversions/simplebot_tgchan.svg
   :target: https://pypi.org/project/simplebot_tgchan

.. image:: https://pepy.tech/badge/simplebot_tgchan
   :target: https://pepy.tech/project/simplebot_tgchan

.. image:: https://img.shields.io/pypi/l/simplebot_tgchan.svg
   :target: https://pypi.org/project/simplebot_tgchan

.. image:: https://github.com/simplebot-org/simplebot_tgchan/actions/workflows/python-ci.yml/badge.svg
   :target: https://github.com/simplebot-org/simplebot_tgchan/actions/workflows/python-ci.yml

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

A `SimpleBot`_ plugin that allows to subscribe to Telegram channels from Delta Chat.

Install
-------

To install run::

  pip install simplebot-tgchan

Configuration
-------------

See https://github.com/simplebot-org/simplebot to know how to configure the bot with an e-mail account.

Before you start using the bot, you need to get your own API ID and hash, go to https://my.telegram.org/
and get them then configure the bot::

    simplebot -a bot@example.com db -s simplebot_tgchan/api_id "12345"
    simplebot -a bot@example.com db -s simplebot_tgchan/api_hash "0123456789abcdef"

Then you must provide a phone number for the bot to use, to start session in Telegram::

    simplebot -a bot@example.com login

After entering the verification code you received in Telegram or via SMS, start the bot::

    simplebot -a bot@example.com serve

Then you can start subscribing to Telegram channels adding the bot to Delta Chat groups and using
``/sub`` command.

Tweaking Default Configuration
------------------------------

You can tweak the interval (in seconds) the bot checks Telegram channels for new messages::

    simplebot -a bot@example.com db -s simplebot_tgchan/delay 300

By default the bot checks Telegram for new messages every 5 minutes.

You can tweak the maximum size (in bytes) of attachments the bot will download::

    simplebot -a bot@example.com db -s simplebot_tgchan/max_size 5242880

By default the bot will download attachments of up to 5MB.

You can restrict the usage of ``/sub`` and ``/unsub`` commands to bot administrators only::

    simplebot -a bot@example.com db -s simplebot_tgchan/allow_subscriptions 0

By default the bot will allow any user to subscribe to Telegram channels.

To add your address as the bot administrator::

    simplebot -a bot@example.com admin -a me@example.com


.. _SimpleBot: https://github.com/simplebot-org/simplebot
