class GoogleService:
  _service = None

  @staticmethod
  def set_google_service(google_service):
    GoogleService._service = google_service

  @staticmethod
  def get_google_service():
    return GoogleService._service
