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

Configure
---------

See https://github.com/simplebot-org/simplebot to know how to configure the bot with an e-mail account.

Before you start using the bot, you need to get your own API ID and hash, go to https://my.telegram.org/
and get them then configure the bot::

    simplebot -a bot@example.com db -s simplebot_tgchan/api_id "12345"
    simplebot -a bot@example.com db -s simplebot_tgchan/api_hash "0123456789abcdef0123456789abcdef"

Add your e-mail address as the bot administrator so you have access to the administration commands::

    simplebot -a bot@example.com admin -a me@example.com

Then you must provide a Telegram account for the bot to use, to start session in Telegram::

    simplebot -a bot@example.com login

After entering phone number and the verification code you received in Telegram or via SMS, start the
bot::

    simplebot -a bot@example.com serve

Then you can start subscribing to Telegram channels with ``/sub`` command writting to the bot address
in Delta Chat.


.. _SimpleBot: https://github.com/simplebot-org/simplebot
