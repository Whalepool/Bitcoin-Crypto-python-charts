import logging
import pika
import json
import os
import sys

FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logging.info('Importing utilities..')


def check_envs(envars):

    # Check ENV variables
    errors = 0 
    for v in envars:
        if os.environ.get(v) is not None:
            logger.info('Found env var: '+v)
            pass
        else:
            errors += 1 
            logger.info('Please set a '+v+' envionment variable.')

    if errors > 0:
        sys.exit()


class Notify:   

    def __init__(self):

        # Check ENV variables
        check_envs(['RMQUSER','RMQPASS','RMQHOST','RMQPORT','RMQVHOST','RMQSOCKETTIMEOUT'])

        self.RMQUSER = os.environ.get('RMQUSER')
        self.RMQPASS = os.environ.get('RMQPASS')
        self.RMQHOST = os.environ.get('RMQHOST')
        self.RMQPORT = os.environ.get('RMQPORT')
        self.RMQVHOST = os.environ.get('RMQVHOST')
        self.RMQSOCKETTIMEOUT = os.environ.get('RMQSOCKETTIMEOUT')



    def teamspeak(self, msg):

        # Connect to rabbitmq
        parameters = pika.URLParameters('amqp://'+self.RMQUSER+':'+self.RMQPASS+'@'+self.RMQHOST+':'+self.RMQPORT+'/'+self.RMQVHOST+'?socket_timeout='+self.RMQSOCKETTIMEOUT)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='teamspeak')

        if isinstance(msg, list):
            for m in msg:
                logger.info("Sending msg to teamspeak: "+str(m))
                channel.basic_publish(exchange='',routing_key='teamspeak',body=json.dumps(m))

        else: 
            logger.info("Sending msg to teamspeak: "+str(msg))
            channel.basic_publish(exchange='',routing_key='teamspeak',body=json.dumps(msg))

        connection.close()


    def telegram(self, msg):
        """
            REQUIRED msg params:
            chat_id: int, telegram user chat id
            message: string, message to be sent 
            
            Optional:
            Markdown: bool, if markdown should be parsed or not
            disable_web_page_preview: bool, if preview should be sent or not

            Changes
            1) picture: path of picture to be sent
            2) sticker: file id of sticker to be sent (sends message after sticker)

        """
        # Connect to rabbitmq
        parameters = pika.URLParameters('amqp://'+self.RMQUSER+':'+self.RMQPASS+'@'+self.RMQHOST+':'+self.RMQPORT+'/'+self.RMQVHOST+'?socket_timeout='+self.RMQSOCKETTIMEOUT)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='telegram')

        if isinstance(msg, list):
            for m in msg:
                logger.info("Sending msg to telegram: "+str(m))
                channel.basic_publish(exchange='',routing_key='telegram',body=json.dumps(m))
                
        else:
            logger.info("Sending msg to telegram: "+str(msg))
            channel.basic_publish(exchange='',routing_key='telegram',body=json.dumps(msg))

        connection.close()



#####################
# MAIN
#####################
check_envs( ['GUSERNAME','GPASS','TS_IP','TS_USERNAME','TS_PASSWORD'] )