
from django.http import HttpResponse
import firebase_admin
from firebase_admin import credentials, firestore, messaging
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response

cred = credentials.Certificate("mysite/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection('shops')


def index(request):
    #accessing our firebase data and storing it in a variable
    docs = users_ref.stream()
    list = []
    for doc in docs:
        list.append(doc.to_dict())
    return HttpResponse(json.dumps(list))

@api_view(['POST'])
def sendNotification(request):
    print(request.data)
    # This registration token comes from the client FCM SDKs.
    registration_tokens = []
    transaction = request.data.get('transaction')
    print(transaction)
    tokens = request.data.get('tokens')
    for token in json.loads(tokens):
        registration_tokens.append(token)
        print(token)
    transaction_json = json.loads(transaction)
    pushTransactionData(transaction_json, request.data.get('shops'))
    # See documentation on defining a message payload.
    message = messaging.MulticastMessage(
        notification=messaging.Notification('New rescue request', "More info"),
        tokens=registration_tokens,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send_multicast(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    return Response()


def pushTransactionData(transaction, shops):
    pending_transaction_ref = db.collection(u'pending_transactions')
    pending_document = pending_transaction_ref.document()
    pending_document.set({
    u'id': pending_document.id,
    u'userId': transaction.get('userId'),
    u'userFullName': transaction.get('userFullName'),
    u'userPhone': transaction.get('userPhone'),
    u'service': transaction.get('service'),
    u'startTime': transaction.get('startTime'),
    u'content': transaction.get('content'),
    u'address': transaction.get('address'),
    u'userLocation': transaction.get('userLocation'),
    u'userFcmToken': transaction.get('userFcmToken'),
    u'shops': json.loads(shops),
    })

