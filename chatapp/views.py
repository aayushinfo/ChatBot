
from chatapp.task import send_scheduled_message
from rest_framework.response import Response
from rest_framework.views import APIView
from chatapp.models import CustomUser, Messages
from chatapp.serializer import UserSerializer, MessageSerializer, AutoMessageSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from collections import defaultdict
from datetime import datetime
import traceback
class UserSignUp(viewsets.ViewSet):

    @action(methods=['get'], detail=False)
    def user_sign_up(self, request):
        try:
            print('in........')
            print('username',  CustomUser.objects.filter(username=request.data.get('username')).first())
            user = CustomUser.objects.filter(email=request.data.get('email')).first()
            print(user)
            if not user:
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    response = {
                        'code': status.HTTP_200_OK,
                        'status': True,
                        'message': 'User logged successfully',
                        'data': serializer.data,
                        'error': []
                    }
                    return Response(response, status=status.HTTP_200_OK)

                return Response({
                    'code': status.HTTP_400_BAD_REQUEST, 'status': False, "message": serializer.errors,}, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'code': status.HTTP_422_UNPROCESSABLE_ENTITY, 'status': False, "message": "Email is already exists"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            return Response({'code': status.HTTP_500_INTERNAL_SERVER_ERROR, 'status': False,
                             "message": "Something went wrong while user signup.", 'data': [], 'error': str(e)
                             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessageViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=False)
    def get_messages(self, request):
        try:
            messages = Messages.objects.all()
            serializer = MessageSerializer(messages, many=True)
            g_msg = defaultdict(list)
            for msg in serializer.data:
                key = (msg['sender_user'], msg['receiver_user'])
                g_msg[key].append({
                    "message": msg['message'],
                    "created_at": datetime.strptime(msg['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.strptime(msg['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"),
                })

            f_data = []
            for (sender, receiver), msgs in g_msg.items():
                f_data.append({
                    "conversation": f"{sender} -> {receiver}",
                    "messages": msgs
                })

            return Response({
                'code': status.HTTP_200_OK,
                'status': True,
                "message": "Messages fetched successfully",
                'data': f_data,
                'error': []
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'status': False,
                "message": "Something went wrong please check",
                'data': [],
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False)
    def send_message(self, request):
        try:
            data = request.data
            data['sender_user'] = int(request.user.id)
            data['receiver_user'] = data.get('receiver_user')

            replies_message_id = data.get('replies_message')

            if replies_message_id is not None:
                try:
                    replies_message_id = int(replies_message_id)
                    if len(Messages.objects.filter(id=replies_message_id)) == 0:
                        return Response({
                            'code': status.HTTP_400_BAD_REQUEST,
                            'status': False,
                            "message": "replies_message message does not exist",
                            'data': [],
                            'error': []
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data['replies_message'] = replies_message_id
                except ValueError:
                    return Response({
                        'code': status.HTTP_400_BAD_REQUEST,
                        'status': False,
                        "message": "replies_message message ID must be an integer",
                        'data': [],
                        'error': []
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['replies_message'] = None

            serializer = MessageSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': status.HTTP_201_CREATED,
                    'status': True,
                    "message": "Message sent successfully",
                    'data': serializer.data,
                    'error': []
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'status': False,
                    "message": "Invalid data",
                    'data': [],
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'status': False,
                "message": "Something went wrong.",
                'data': [],
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class AutoMessageView(viewsets.ViewSet):
    @action(methods=['post'], detail=False)
    def send_message(self, request):
        try:
            data = request.data

            # Ensure sender_user is properly assigned
            if request.user and hasattr(request.user, 'id'):
                data['sender_user'] = int(request.user.id)
            else:
                return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'status': False,
                    "message": "Sender user is not authenticated.",
                    'data': [],
                    'error': []
                }, status=status.HTTP_400_BAD_REQUEST)

            receiver_user = data.get('receiver_user')
            if receiver_user is None:
                return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'status': False,
                    "message": "Receiver user must be provided.",
                    'data': [],
                    'error': []
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['receiver_user'] = int(receiver_user)

            replies_message_id = data.get('replies_message')

            if replies_message_id is not None:
                try:
                    replies_message_id = int(replies_message_id)
                    if not Messages.objects.filter(id=replies_message_id).exists():
                        return Response({
                            'code': status.HTTP_400_BAD_REQUEST,
                            'status': False,
                            "message": "Replies message does not exist.",
                            'data': [],
                            'error': []
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data['replies_message'] = replies_message_id
                except ValueError:
                    return Response({
                        'code': status.HTTP_400_BAD_REQUEST,
                        'status': False,
                        "message": "Replies message ID must be an integer.",
                        'data': [],
                        'error': []
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['replies_message'] = None

            # Extract send_time from data if present
            send_time_str = data.get('send_time')
            print(send_time_str)
            if send_time_str:
                # del data['send_time']
                pass

            serializer = AutoMessageSerializer(data=data)

            if serializer.is_valid():
                message = serializer.save()

                # Schedule the message if send_time is provided
                if send_time_str:
                    try:
                        send_time = datetime.strptime(send_time_str, '%Y-%m-%d %H:%M:%S')
                        delay = (send_time - datetime.now()).total_seconds()
                        if delay > 0:
                            send_scheduled_message.apply_async((message.id,), countdown=delay)
                        else:
                            return Response({
                                'code': status.HTTP_400_BAD_REQUEST,
                                'status': False,
                                "message": "Send time must be in the future.",
                                'data': [],
                                'error': []
                            }, status=status.HTTP_400_BAD_REQUEST)
                    except ValueError:
                        return Response({
                            'code': status.HTTP_400_BAD_REQUEST,
                            'status': False,
                            "message": "Send time format is incorrect.",
                            'data': [],
                            'error': []
                        }, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    'code': status.HTTP_201_CREATED,
                    'status': True,
                    "message": "Message sent successfully",
                    'data': serializer.data,
                    'error': []
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'status': False,
                    "message": "Invalid data",
                    'data': [],
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'status': False,
                "message": "Something went wrong.",
                'data': [],
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)