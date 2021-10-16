import zipfile
from typing import Optional

from lxml import etree
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _is_valid_info(info):
    return 'com.microsoft.__Attachments' not in info and 'message_' not in info


def make_email(headers, body, attachments):
    msg = MIMEMultipart()
    for header in headers.keys():
        if isinstance(headers[header], str):
            msg[header] = headers[header]
        elif isinstance(headers[header], list):
            msg[header] = ', '.join(headers[header])

    if body is not None:
        if 'text/html' in body.keys():
            email = MIMEText(body['text/html'], 'html')
        elif 'text/plain' in body.keys():
            email = MIMEText(body['text/plain'], 'plain')
        else:
            raise AttributeError("Unknown email encoding in '%s'" % body.keys())
        msg.attach(email)
    if attachments is not []:
        # TODO
        pass

    return msg


class OlmParser:
    _olm_file_path: str
    _zip_file: zipfile.ZipFile
    _name_list: list[str]

    def __init__(self, olm_file_path: str):
        self._olm_file_path = olm_file_path
        self._zip_file = zipfile.ZipFile(self._olm_file_path, 'r')
        self._name_list = self._zip_file.namelist()

    def count(self):
        if not self._name_list:
            return 0
        else:
            return len(self._name_list)

    def get_info_at_index(self, index):
        if not self._name_list or index >= len(self._name_list):
            return None
        else:
            return self._name_list[index]

    def _dump_tags(self, tree):
        print('----------')
        for tag in tree.getchildren():
            print(tag)

    def _load_attachment(self, zip_file, name):
        fh = zip_file.open(name)
        return fh

    def _get_id(self, email):
        tag_id = email.find('.//OPFMessageCopyMessageID')
        if tag_id is None:
            tag_id = email.find('.//OPFMessageCopyExchangeConversationId')
        return tag_id.text.strip()

    def _get_date(self, email):
        tag = email.find('.//OPFMessageCopySentTime')
        if tag is None:
            tag = email.find('.//OPFMessageCopyReceivedTime')
        date = datetime.strptime(tag.text.strip(), '%Y-%m-%dT%H:%M:%S')
        return date.isoformat()

    def _get_body(self, email):
        has_html = email.find('.//OPFMessageGetHasHTML')
        # has_rich = email.find('.//OPFMessageGetHasRichText')
        tag_body = email.find('.//OPFMessageCopyBody')
        mime_type = 'text/plain'
        if has_html is not None:
            html = has_html.text.replace('E0', '')
            if html == '1':
                tag_body = email.find('.//OPFMessageCopyHTMLBody')
                mime_type = 'text/html'

        if tag_body is None:
            body = ""
        else:
            body = tag_body.text
            if body is not None:
                # There might be no body if it's a calender reply or something.
                # Calendar replies still have subject lines and addressees and stuff
                # though so probably worth keeping.
                body = body.strip().encode('utf-8')

        return {mime_type: body}

    def _get_attachments(self, zip_file, email):
        attachments = []
        tag_attachments = email.find('.//OPFMessageCopyAttachmentList')
        if tag_attachments is not None:
            for attachment in tag_attachments.findall('.//messageAttachment'):
                name = attachment.get('OPFAttachmentName')
                mime_type = attachment.get('OPFAttachmentContentType')
                # extension = attachment.get('OPFAttachmentContentExtension')
                # id = attachment.get('OPFAttachmentContentID')
                file = {
                    'file_name': name,
                    'mime_type': mime_type
                }
                url = attachment.get('OPFAttachmentURL')
                if url is not None:
                    fh = self._load_attachment(zip_file, url)
                    file['file_path'] = url
                    file['file_handle'] = fh
                attachments.append(file)
        return attachments

    def _get_addresses(self, email):
        tag_from = email.find('.//OPFMessageCopyFromAddresses')
        tag_sender = email.find('.//OPFMessageCopySenderAddress')
        tag_to = email.find('.//OPFMessageCopyToAddresses')
        tag_cc = email.find('.//OPFMessageCopyCCAddresses')
        tag_bcc = email.find('.//OPFMessageCopyBCCAddresses')

        from_names, from_emails = self._get_contacts(tag_from)
        sender_names, sender_emails = self._get_contacts(tag_sender)
        to_names, to_emails = self._get_contacts(tag_to)
        cc_names, cc_emails = self._get_contacts(tag_cc)
        bcc_names, bcc_emails = self._get_contacts(tag_bcc)

        names = to_names + from_names + cc_names + bcc_names + sender_names
        emails = to_emails + from_emails + cc_emails + bcc_emails + sender_emails

        frm = from_emails + sender_emails
        author = from_names + sender_names

        return names, emails, author, frm, to_emails, cc_emails, bcc_emails

    def _get_contacts(self, addresses):
        names = []
        emails = []
        if addresses is not None:
            for address in addresses.findall('.//emailAddress'):
                email = address.get('OPFContactEmailAddressAddress')
                if email is not None:
                    emails.append(email)
                name = address.get('OPFContactEmailAddressName')
                if name is not None and name != email:
                    names.append(name)

                # etype = address.get('OPFContactEmailAddressType')

        return names, emails

    def parse_message(self, name):
        headers = {
            'From': None,
            'To': None,
            'Subject': None,
            'Message-ID': None,
            'CC': None,
            'BCC': None,
            'Date': None,
        }
        body = None
        attachments = []
        names = []
        emails = []
        title = None
        author = None

        doc = None
        fh = self._zip_file.open(name)
        try:
            doc = etree.parse(fh)
        except etree.XMLSyntaxError:
            p = etree.XMLParser(huge_tree=True)
            try:
                doc = etree.parse(fh, p)
            except etree.XMLSyntaxError:
                # probably corrupt
                pass

        if doc is None:
            return

        for email in doc.findall('//email'):

            headers['Message-ID'] = self._get_id(email)
            headers['Date'] = self._get_date(email)

            tag_subject = email.find('.//OPFMessageCopySubject')
            # OPFMessageCopyThreadTopic
            if tag_subject is not None:
                headers['Subject'] = title = tag_subject.text.strip()

            names, emails, author, frm, to, cc, bcc = self._get_addresses(email)
            headers['To'] = to
            headers['From'] = frm
            headers['CC'] = cc
            headers['BCC'] = bcc

            body = self._get_body(email)
            attachments = self._get_attachments(self._zip_file, email)

            return {
                'headers': headers,
                'body': body,
                'attachments': attachments,
                'names': names,
                'emails': emails,
                'title': title,
                'author': author,
                'created_at': headers['Date']
            }


class OlmEmailIterator:
    current_index: int
    zip_file_reader: OlmParser

    def __init__(self, zip_file_reader: OlmParser):
        self.current_index = 0
        self.zip_file_reader = zip_file_reader

    def __next__(self) -> MIMEMultipart:
        self._skip_invalid_infos()

        if self._current() is None:
            raise StopIteration

        parsed = self.zip_file_reader.parse_message(self._current())
        email = make_email(parsed['headers'], parsed[
            'body'], parsed['attachments'])

        return email

    def _skip_invalid_infos(self) -> None:
        valid_info_found = False
        while not valid_info_found:
            if self.current_index >= self.zip_file_reader.count():
                break

            if not _is_valid_info(self._current()):
                self.current_index += 1
            else:
                valid_info_found = True

    def _current(self) -> Optional[str]:
        return self.zip_file_reader.get_info_at_index(self.current_index)

    def __iter__(self):
        return self
