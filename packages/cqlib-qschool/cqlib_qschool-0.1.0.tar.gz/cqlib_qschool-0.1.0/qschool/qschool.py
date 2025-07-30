from cqlib.quantum_platform import TianYanPlatform


class QSchoolPlatform(TianYanPlatform):
    """
    Tian yan quantum computing cloud quantum_platform
    """
    SCHEME = 'https'
    DOMAIN = 'qschool.zdxlz.com'
    LOGIN_PATH = '/tri-auth/oauth2/sdk/opnId'
    CREATE_LAB_PATH = '/tri-quantum/sdk/experiment/save'
    SAVE_EXP_PATH = '/tri-quantum/sdk/experiment/detail/save'
    RUN_EXP_PATH = '/tri-quantum/sdk/experiment/detail/run'
    SUBMIT_EXP_PATH = '/tri-quantum/sdk/experiment/submit'
    # create exp and run path
    CREATE_EXP_AND_RUN_PATH = '/tri-quantum/sdk/experiment/temporary/save'
    QUERY_EXP_PATH = '/tri-quantum/sdk/experiment/result/find'
    # download config path
    DOWNLOAD_CONFIG_PATH = '/tri-quantum/sdk/experiment/download/config'
    # qics check regular path
    QCIS_CHECK_REGULAR_PATH = '/tri-quantum/sdk/experiment/qcis/rule/verify'
    # get exp circuit path
    GET_EXP_CIRCUIT_PATH = '/tri-quantum/sdk/experiment/getQcis/by/taskIds'
    # machine list path
    MACHINE_LIST_PATH = '/tri-quantum/sdk/quantumComputer/list'
    # re execute path
    RE_EXECUTE_TASK_PATH = '/tri-quantum/sdk/experiment/resubmit'


