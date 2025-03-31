SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    },
}


# # Swagger Settings
# SWAGGER_SETTINGS = {
#     'USE_SESSION_AUTH': False,
#     'SECURITY_DEFINITIONS': {
#         'Bearer': {
#             'type': 'apiKey',
#             'name': 'Authorization',
#             'in': 'header',
#             'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
#         }
#     },
#     'SECURITY': [
#         {'Bearer': []}
#     ],
#     'DEFAULT_INFO': {
#         'title': 'DDD Attendance Management API',
#         'version': '1.0.0',
#         'description': '''
#             DDD 커뮤니티 출석 관리를 위한 API 서비스입니다.
            
#             ## 주요 기능
#             - JWT 기반 인증
#             - 소셜 로그인 (Google, Kakao)
#             - QR 코드 생성 및 검증
#             - 프로필 관리
#             - 초대 시스템
#             - 일정 관리
            
#             ## 응답 형식
#             모든 API 응답은 다음 형식을 따릅니다:
#             ```json
#             {
#               "code": 200,
#               "message": "작업 성공 메시지",
#               "data": { ... }
#             }
#             ```
            
#             ## 에러 코드
#             - 200: 성공
#             - 201: 생성 성공
#             - 400: 잘못된 요청
#             - 401: 인증 실패
#             - 403: 권한 없음
#             - 404: 리소스 없음
#             - 500: 서버 에러
#         ''',
#         'terms_of_service': 'https://www.google.com/policies/terms/',
#         'contact': {
#             'name': 'DDD Team',
#             'email': 'cfi02222@gmail.com'
#         },
#         'license': {
#             'name': 'MIT License'
#         }
#     },
#     'DEFAULT_API_URL': '/api/v1/',
#     'DEFAULT_FIELD_INSPECTORS': [
#         'drf_yasg.inspectors.CamelCaseJSONFilter',
#         'drf_yasg.inspectors.ReferencingSerializerInspector',
#         'drf_yasg.inspectors.RelatedFieldInspector',
#         'drf_yasg.inspectors.ChoiceFieldInspector',
#         'drf_yasg.inspectors.FileFieldInspector',
#         'drf_yasg.inspectors.DictFieldInspector',
#         'drf_yasg.inspectors.SimpleFieldInspector',
#         'drf_yasg.inspectors.StringDefaultFieldInspector',
#     ],
#     'DEFAULT_PAGINATOR_INSPECTORS': [
#         'drf_yasg.inspectors.DjangoRestResponsePagination',
#         'drf_yasg.inspectors.CoreAPICompatInspector',
#     ],
#     'TAGS_SORTER': 'alpha',
#     'OPERATIONS_SORTER': 'alpha',
#     'TAGS': [
#         {'name': 'health', 'description': '서버 상태 확인 관련 작업'},
#         {'name': 'auth', 'description': '사용자 인증 관련 작업'},
#         {'name': 'invites', 'description': '초대코드 관련 작업'},
#         {'name': 'users', 'description': '사용자 등록 및 관리 관련 작업'},
#         {'name': 'qr', 'description': 'QR 코드 관련 작업'},
#         {'name': 'schedules', 'description': '스케쥴 관련 작업'},
#         {'name': 'attendance', 'description': '출석 관련 작업'},
#     ],
# }