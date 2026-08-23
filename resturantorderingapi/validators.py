from html import unescape

from rest_framework import serializers


def validate_no_html(value):
    if value in (None, ""):
        return value

    decoded_value = unescape(value)
    if "<" in decoded_value or ">" in decoded_value:
        raise serializers.ValidationError("HTML is not allowed.")

    return value
