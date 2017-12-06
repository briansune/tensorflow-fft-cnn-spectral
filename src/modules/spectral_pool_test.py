import numpy as np
import tensorflow as tf


def tfshift(matrix, n, axis=1):
    mid = (n + 1) // 2
    if axis == 1:
        start = [0, mid, 0]
        end = [-1, mid, -1]
    else:
        start = [mid, 0, 0]
        end = [mid, -1, -1]
    out = tf.concat([tf.slice(matrix, start, [-1, -1, -1]),
                     tf.slice(matrix, [0, 0, 0], end)], axis)
    return out


def tfroll(matrix, n):
    mat = tfshift(matrix, n, 1)
    mat2 = tfshift(mat, n, 0)
    return mat2


def spectral_pool(image, pool_size=4,
                  convert_grayscale=True):
    """ Perform a single spectral pool operation.
    Args:
        image: 2D image, same height and width
        pool_size: number of dimensions to throw away in each dimension
    """
    n = image.shape[0]
    im = tf.placeholder(shape=(n, n, 3), dtype=tf.float32)
    if convert_grayscale:
        im_conv = tf.image.rgb_to_grayscale(im)
    else:
        im_conv = im
    im_fft = tf.fft(tf.cast(im_conv, tf.complex64))
    im_fft_roll = tfroll(im_fft, n)
    print(im_fft_roll.get_shape())
    target_size = n - pool_size
    # crop the extra dimensions centrally
    im_crop = tf.image.resize_image_with_crop_or_pad(image=im_fft_roll,
                                                     target_height=target_size,
                                                     target_width=target_size)
    # pad with 0s to get the original size
    # im_pad = tf.image.resize_image_with_crop_or_pad(image=im_crop,
    #                                                  target_height=n,
    #                                                  target_width=n)
    print(im_crop.get_shape())
    n = im_crop.get_shape().as_list()[0]
    im_unroll = tfroll(im_crop, n)
    print(im_unroll.get_shape())
    im_transformed = tf.ifft(im_unroll)

    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)
        im_fftout, im_new = sess.run([im_fft_roll, im_transformed],
                                     feed_dict={im: image})

    return im_fftout, im_new


def max_pool(image, pool_size=4,
             convert_grayscale=True):
    im = image.convert('F')
    im_np = np.asarray(im)
    imsize = im_np.shape[0]

    im_new = im_np.copy()
    for i in range(0, imsize, pool_size):
        for j in range(0, imsize, pool_size):
            max_val = np.max(im_new[i: i + pool_size, j: j + pool_size])
            im_new[i: i + pool_size, j: j + pool_size] = max_val
    return im_new