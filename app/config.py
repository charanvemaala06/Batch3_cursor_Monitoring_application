import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 1800

    # Local HTTP demo: Secure=False. Production behind HTTPS should set True.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() in (
        '1',
        'true',
        'yes',
    )

    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

    SERVERS_FILE = os.getenv(
        'SERVERS_FILE',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'servers.json'),
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-secret-key-not-for-production'
    ADMIN_USERNAME = 'admin'
    # password: testpass
    ADMIN_PASSWORD_HASH = (
        'scrypt:32768:8:1$1gMPapCvvTtRUX9s$'
        'd0b84f167669e9fe1e971d0dc2d92edfe756ab2871af7ac2a315d6f766a39ba8'
        'feaeac9b4eb50566191a19ca7037f04f80d60128dce6b4fcd2883c9de016dd64'
    )
    SESSION_TYPE = 'filesystem'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
