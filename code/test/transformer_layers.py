import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import (
    Layer,
    Dense,
    Dropout,
    LayerNormalization
)


@tf.keras.utils.register_keras_serializable()
class TransformerEncoder(Layer):
    def __init__(self, embed_dim=128, num_heads=32,
                 ff_dim=2048, dropout=0.1, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.dropout_rate = dropout

        self.attention = tf.keras.layers.MultiHeadAttention(
            num_heads=num_heads,
            key_dim=embed_dim // num_heads
        )
        self.ffn = Sequential([
            Dense(ff_dim, activation="relu"),
            Dense(embed_dim)
        ])
        self.norm1 = LayerNormalization()
        self.norm2 = LayerNormalization()
        self.dropout1 = Dropout(dropout)
        self.dropout2 = Dropout(dropout)

    def call(self, x, training=None):
        attention = self.attention(x, x)
        x = self.norm1(
            x + self.dropout1(attention, training=training)
        )
        output = self.ffn(x)
        return self.norm2(
            x + self.dropout2(output, training=training)
        )

    def get_config(self):
        config = super().get_config()
        config.update({
            "embed_dim": self.embed_dim,
            "num_heads": self.num_heads,
            "ff_dim": self.ff_dim,
            "dropout": self.dropout_rate
        })
        return config


@tf.keras.utils.register_keras_serializable()
class PositionalEncoding(Layer):
    def call(self, x):
        length = tf.shape(x)[1]
        depth = tf.shape(x)[2]

        positions = tf.cast(
            tf.range(length)[:, None],
            tf.float32
        )
        depths = tf.cast(
            tf.range(0, depth, 2)[None, :],
            tf.float32
        )
        angles = positions / tf.pow(
            10000.0,
            depths / tf.cast(depth, tf.float32)
        )
        encoding = tf.reshape(
            tf.stack(
                [tf.sin(angles), tf.cos(angles)],
                axis=-1
            ),
            (length, depth)
        )
        return x + encoding[None, :, :]