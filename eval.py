"""
License: Apache-2.0
Author: Suofei Zhang | Hang Yu
E-mail: zhangsuofei at njupt.edu.cn | hangyu5 at illinois.edu
"""

import tensorflow as tf
from config import cfg, get_coord_add, get_dataset_size_train, get_dataset_size_test, get_num_classes, get_create_inputs
import time
import numpy as np
import os
import capsnet_em as net

import logging
import daiquiri

daiquiri.setup(level=logging.DEBUG)
logger = daiquiri.getLogger(__name__)


def main(dataset_name: str):
    """Get dataset hyperparameters."""
    coord_add = get_coord_add(dataset_name)
    dataset_size_train = get_dataset_size_train(dataset_name)
    dataset_size_test = get_dataset_size_test(dataset_name)
    num_classes = get_num_classes(dataset_name)
    create_inputs = get_create_inputs(
        dataset_name, is_train=False, epochs=cfg.epochs)

    """Set reproduciable random seed"""
    tf.set_random_seed(1234)

    with tf.Graph().as_default():
        num_batches_per_epoch_train = int(dataset_size_train / cfg.batch_size)
        num_batches_test = int(dataset_size_test / cfg.batch_size)

        batch_x, batch_labels = create_inputs()
        output = net.build_arch(batch_x, coord_add, is_train=False)
        batch_acc = net.test_accuracy(output, batch_labels)
        saver = tf.train.Saver()

        step = 0

        summaries = []
        summaries.append(tf.summary.scalar('accuracy', batch_acc))
        summary_op = tf.summary.merge(summaries)

        with tf.Session() as sess:
            tf.train.start_queue_runners(sess=sess)
            summary_writer = tf.summary.FileWriter(
                cfg.test_logdir, graph=None)  # graph=sess.graph, huge!

            for epoch in range(cfg.epoch):
                ckpt = os.path.join(cfg.logdir, 'model.ckpt-%d' %
                                    (num_batches_per_epoch_train * epoch))
                saver.restore(sess, ckpt)

                accuracy_sum = 0
                for i in range(num_batches_test):
                    batch_acc_v, summary_str = sess.run([batch_acc, summary_op])
                    print('%d batches are tested.' % step)
                    summary_writer.add_summary(summary_str, step)

                    accuracy_sum += batch_acc_v

                    step += 1

                ave_acc = accuracy_sum / num_batches_test
                print('the average accuracy is %f' % ave_acc)


if __name__ == "__main__":
    tf.app.run()
