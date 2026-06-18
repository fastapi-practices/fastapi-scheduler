declare namespace Api {
  /**
   * namespace Auth
   *
   * backend api module: "auth"
   */
  namespace Auth {
    interface LoginToken {
      access_token: string;
      access_token_expire_time: string;
      session_uuid: string;
      password_expire_days_remaining?: number | null;
      user: GetUserInfoDetail;
    }

    interface NewToken {
      access_token: string;
      access_token_expire_time: string;
      session_uuid: string;
    }

    interface UserInfo {
      userId: string;
      userName: string;
      roles: string[];
      buttons: string[];
      nickname?: string;
      avatar?: string;
      email?: string;
      phone?: string;
      isSuperuser?: boolean;
      isStaff?: boolean;
    }

    interface GetUserInfoDetail {
      id: number;
      uuid: string;
      username: string;
      nickname: string;
      avatar?: string | null;
      email?: string | null;
      phone?: string | null;
      status: number;
      is_superuser: boolean;
      is_staff: boolean;
      is_multi_login: boolean;
    }

    interface CaptchaInfo {
      is_enabled: boolean;
      expire_seconds: number;
      uuid: string;
      image: string;
    }
  }
}
