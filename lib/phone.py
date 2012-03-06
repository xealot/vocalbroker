import phonenumbers

def convert_to_e164(raw_phone):
    if not raw_phone:
        return

    if raw_phone[0] == '+':
        # Phone number may already be in E.164 format.
        parse_type = None
    else:
        # Assume it's a US number
        parse_type = "US"

    phone_representation = phonenumbers.parse(raw_phone, parse_type)
    return phonenumbers.format_number(phone_representation,
        phonenumbers.PhoneNumberFormat.E164)