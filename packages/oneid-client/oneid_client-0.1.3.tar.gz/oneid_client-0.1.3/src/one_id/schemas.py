from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LegalInfo:
    is_basic: bool
    tin: str
    acron_UZ: str
    le_tin: str
    le_name: str


@dataclass
class AuthMethod:
    login_pass: str
    mobile: str
    pkcs: str
    lepkcs: str


@dataclass
class User:
    user_id: Optional[str] = None
    user_type: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    sur_name: Optional[str] = None
    mid_name: Optional[str] = None
    full_name: Optional[str] = None
    mob_phone_no: Optional[str] = None
    birth_date: Optional[str] = None
    tem_adr: Optional[str] = None
    gd: Optional[str] = None
    per_adr: Optional[str] = None
    birth_place: Optional[str] = None
    birth_cntry: Optional[str] = None
    natn: Optional[str] = None
    ctzn: Optional[str] = None
    pport_issue_place: Optional[str] = None
    pport_issue_date: Optional[str] = None
    pport_expr_date: Optional[str] = None
    ret_cd: Optional[str] = None
    valid: Optional[bool] = None
    pin: Optional[str] = None
    tin: Optional[str] = None
    pport_no: Optional[str] = None
    sess_id: Optional[str] = None
    legal_info: Optional[List['LegalInfo']] = None
    auth_method: Optional[List['AuthMethod']] = None
    valid_methods: Optional[List] = None
