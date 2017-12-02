# coding=utf-8

from kafka import KafkaConsumer

consumer = KafkaConsumer('CDC', bootstrap_servers='ec2-54-223-226-77.cn-north-1.compute.amazonaws.com.cn:9092', group_id='cdcgrp')
for msg in consumer:
    print(msg)
