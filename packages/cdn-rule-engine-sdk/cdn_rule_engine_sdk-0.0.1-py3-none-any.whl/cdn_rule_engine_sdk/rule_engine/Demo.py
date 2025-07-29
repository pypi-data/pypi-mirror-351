# coding: utf-8
from rule_engine.Rule import Action, BaseCondition

def action_allow_access() -> Action:
    """
    动作: 允许访问
    :return: Action
    """
    action = Action({
        "Action": "allow_access",
        "Groups": [{
            "Dimension": "allow_access",
            "GroupParameters": []
        }]
    })
    return action

def action_deny_access() -> Action:
    """
    动作: 禁止访问，返回403
    :return: Action
    """
    action = Action({
        "Action": "deny_access",
        "Groups": [{
            "Dimension": "deny_access",
            "GroupParameters": [{
                "Parameters": [{
                    "Name": "status_code",
                    "Values": ["403"]
                }]
            }]
        }]
    })
    return action

def action_redirect_request() -> Action:
    """
    动作: 重定向改写，将原始请求地址 /path_source?a=1&b=2&c=3 重定向到 https://www.test.com/path_target?a=1&b=2，仅保留 a 和 b 两个参数
    :return: Action
    """
    action = Action({
        "Action": "redirect_request",
        "Groups": [{
            "Dimension": "redirect_request",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"source_path",
                        "Values": ["/path_source"]
                    },
                    {
                        "Name":"target_path",
                        "Values": ["/path_target"]
                    },
                    {
                        "Name":"status_code",
                        "Values": ["302"]
                    },
                    {
                        "Name":"protocol",
                        "Values": ["https"]
                    },
                    {
                        "Name":"target_host",
                        "Values": ["www.test.com"]
                    },
                    {
                        "Name":"target_query_action",
                        "Values": ["include_part"]
                    },
                    {
                        "Name":"target_query_values",
                        "Values": ["a", "b"]
                    }
                ]
            }]
        }]
    })
    return action

def action_redirect_protocol() -> Action:
    """
    动作： 协议强制跳转，将 http 协议强制跳转为 https 协议，301 跳转
    :return: Action
    """
    action = Action({
        "Action":"redirect_protocol",
        "Groups": [{
            "Dimension":"redirect_protocol",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"status_code",
                        "Values": ["301"]
                    },
                    {
                        "Name":"protocol",
                        "Values": ["https"]
                    }
                ]
            }]
        }]
    })
    return action

def action_download_speed_limit() -> Action:
    """
    动作： 限速，限速 100KB/s，仅在文件大小超过 1000MB 后限速
    :return: Action
    """
    action = Action({
        "Action":"download_speed_limit",
        "Groups": [{
            "Dimension":"download_speed_limit",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"rate",
                        "Values": ["100"]
                    },
                    {
                        "Name":"rate_unit",
                        "Values": ["KB/s"]
                    },
                    {
                        "Name": "after_size",
                        "Values": ["1000"]
                    },
                    {
                        "Name": "after_size_unit",
                        "Values": ["MB"]
                    }
                ]
            }]
        }]
    })
    return action

def action_response_header() -> Action:
    """
    动作： 响应头改写，将客户端响应头 X-H1 改为 X-H2
    :return: Action
    """
    action = Action({
        "Action":"response_header",
        "Groups": [{
            "Dimension":"response_header",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name": "action",
                        "Values": ["set"]
                    },
                    {
                        "Name":"header_name",
                        "Values": ["X-H1"]
                    },
                    {
                        "Name":"header_value",
                        "Values": ["X-H2"]
                    }
                ]
            }]
        }]
    })
    return action

def action_request_header() -> Action:
    """
    动作： 请求头改写，将客户端请求头 X-H1 改为 X-H2
    :return: Action
    """
    action = Action({
        "Action":"request_header",
        "Groups": [{
            "Dimension":"request_header",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name": "action",
                        "Values": ["set"]
                    },
                    {
                        "Name":"header_name",
                        "Values": ["X-H1"]
                    },
                    {
                        "Name":"header_value",
                        "Values": ["X-H2"]
                    }
                ]
            }]
        }]
    })
    return action

def action_cache_key() -> Action:
    """
    动作： 缓存键改写，"将缓存键改写为包含以下字段：
    - 查询字符串：缓存键参数部分仅保留 a 和 b 两个参数
    - 请求路径：缓存键路径部分，将原始请求路径 /path_source 改写为 /path_target
    - 请求头: 取 X-H1 头部值计算缓存键，并忽略大小写
    - Cookie：取 Cookie 中的 c1 和 c2 计算缓存键，并忽略大小写"
    :return: Action
    """
    action = Action({
        "Action":"cache_key",
        "Groups": [
            {
                "Dimension":"query_string",
                "GroupParameters": [{
                    "Parameters": [
                        {
                            "Name": "query_action",
                            "Values": ["include_part"]
                        },
                        {
                            "Name":"query_names",
                            "Values": ["a", "b"]
                        },
                        {
                            "Name":"ignore_case",
                            "Values": ["false"]
                        }
                    ]
                }]
            },
            {
                "Dimension":"request_path",
                "GroupParameters": [{
                    "Parameters": [
                        {
                            "Name": "source_path",
                            "Values": ["/path_source"]
                        },
                        {
                            "Name":"target_path",
                            "Values": ["/path_target"]
                        }
                    ]
                }]
            },
            {
                "Dimension":"request_header",
                "GroupParameters": [{
                    "Parameters": [
                        {
                            "Name": "header_names",
                            "Values": ["X-H1"]
                        },
                        {
                            "Name":"ignore_case",
                            "Values": ["true"]
                        }
                    ]
                }]
            },
            {
                "Dimension":"cookie",
                "GroupParameters": [{
                    "Parameters": [
                        {
                            "Name":"cookie_action",
                            "Values": ["include_part"]
                        },
                        {
                            "Name":"cookie_names",
                            "Values": ["c1", "c2"]
                        },
                        {
                            "Name":"ignore_case",
                            "Values": ["true"]
                        }
                    ]
                }]
            }
        ]
    })
    return action

def action_compression() -> Action:
    """
    动作： 压缩，开启 gzip+brotli 压缩，仅在文件大小超过 1000MB 后压缩，要压缩的文件类型为 html、js、css、json
    :return: Action
    """
    action = Action({
        "Action":"compression",
        "Groups": [{
            "Dimension":"compression",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"methods",
                        "Values": ["gzip", "brotli"]
                    },
                    {
                        "Name":"min_file_size",
                        "Values": ["1000"]
                    },
                    {
                        "Name":"min_file_size_unit",
                        "Values": ["MB"]
                    },
                    {
                        "Name":"format",
                        "Values": ["customize"]
                    },
                    {
                        "Name":"content_types",
                        "Values": ["text/html", "application/javascript", "text/css", "application/json"]
                    }
                ]
            }]
        }]
    })
    return action

def action_video_drag() -> Action:
    """
    动作： 视频拖拽，开启视频拖拽
    :return: Action
    """
    action = Action({
        "Action":"video_drag",
        "Groups": [{
            "Dimension":"video_drag",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"switch",
                        "Values": ["true"]
                    },
                ]
            }]
        }]
    })
    return action

def action_origin_range() -> Action:
    """
    动作： Range回源，开启Range回源
    :return: Action
    """
    action = Action({
        "Action":"origin_range",
        "Groups": [{
            "Dimension":"origin_range",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"switch",
                        "Values": ["true"]
                    },
                ]
            }]
        }]
    })
    return action

def action_origin_follow() -> Action:
    """
    动作： 回源重定向跟随，开启回源重定向跟随
    :return: Action
    """
    action = Action({
        "Action":"origin_follow",
        "Groups": [{
            "Dimension":"origin_follow",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"switch",
                        "Values": ["true"]
                    },
                ]
            }]
        }]
    })
    return action

def action_origin_tcp_timeout() -> Action:
    """
    动作： 回源超时时间，将回源连接超时时间设置为 10s
    :return: Action
    """
    action = Action({
        "Action":"origin_tcp_timeout",
        "Groups": [{
            "Dimension":"origin_tcp_timeout",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"connect_timeout",
                        "Values": ["10"]
                    },
                    {
                        "Name":"connect_timeout_unit",
                        "Values": ["sec"]
                    },
                ]
            }]
        }]
    })
    return action

def action_origin_http_timeout() -> Action:
    """
    动作： 回源超时时间，将回源响应超时时间设置为 10s
    :return: Action
    """
    action = Action({
        "Action":"origin_http_timeout",
        "Groups": [{
            "Dimension":"origin_http_timeout",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"read_timeout",
                        "Values": ["10"]
                    },
                    {
                        "Name":"read_timeout_unit",
                        "Values": ["sec"]
                    },
                ]
            }]
        }]
    })
    return action

def action_origin_response_header() -> Action:
    """
    动作： 回源响应头改写，将回源响应头 X-H1 改为 X-H2
    :return: Action
    """
    action = Action({
        "Action":"origin_response_header",
        "Groups": [{
            "Dimension":"origin_response_header",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name": "action",
                        "Values": ["set"]
                    },
                    {
                        "Name":"header_name",
                        "Values": ["X-H1"]
                    },
                    {
                        "Name":"header_value",
                        "Values": ["X-H2"]
                    }
                ]
            }]
        }]
    })
    return action

def action_origin_request_header() -> Action:
    """
    动作： 回源请求头改写，将回源请求头 X-H1 改为 X-H2
    :return: Action
    """
    action = Action({
        "Action":"origin_request_header",
        "Groups": [{
            "Dimension":"origin_request_header",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name": "action",
                        "Values": ["set"]
                    },
                    {
                        "Name":"header_name",
                        "Values": ["X-H1"]
                    },
                    {
                        "Name":"header_value",
                        "Values": ["X-H2"]
                    }
                ]
            }]
        }]
    })
    return action

def action_cache_time() -> Action:
    """
    动作： 缓存时间，将缓存时间设置为 10分钟；缓存策略为遵循源站优先，并补充缓存
    :return: Action
    """
    action = Action({
        "Action":"cache_time",
        "Groups": [{
            "Dimension":"cache_time",
            "GroupParameters": [{
                "Parameters": [
                    {
                        "Name":"ttl",
                        "Values": ["10"]
                    },
                    {
                        "Name":"ttl_unit",
                        "Values": ["min"]
                    },
                    {
                        "Name":"cache_policy",
                        "Values": ["origin_first"]
                    },
                    {
                        "Name":"replenish",
                        "Values": ["true"]
                    }
                ]
            }]
        }]
    })
    return action

def condition_always() -> BaseCondition:
    """
    条件： 总是满足
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "always",
    })
    return condition

def condition_path() -> BaseCondition:
    """
    条件： 路径匹配，等于 /path_source1 或 /path_source2，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "path",
        "Operator": "equal",
        "Value": ["/path_source1", "/path_source2"],
        "IgnoreCase": True
    })
    return condition

def condition_path_and_param() -> BaseCondition:
    """
    条件： 路径和参数匹配，等于 /path1?a=1 或 /path2?b=2，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "path_and_param",
        "Operator": "equal",
        "Value": ["/path1?a=1", "/path2?b=2"],
        "IgnoreCase": True
    })
    return condition

def condition_url() -> BaseCondition:
    """
    条件： URL匹配，等于 http://www.test.com/path1?a=1，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "url",
        "Operator": "equal",
        "Value": ["http://www.test.com/path1?a=1"],
        "IgnoreCase": True
    })
    return condition

def condition_query_string() -> BaseCondition:
    """
    条件： 查询字符串匹配，参数a 等于 1 或 2，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "query_string",
        "Operator": "equal",
        "Value": ["1", "2"],
        "IgnoreCase": True,
        "Name": "a"
    })
    return condition

def condition_http_referer() -> BaseCondition:
    """
    条件： HTTP Referer 匹配，等于 www.test.com，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "http_referer",
        "Operator": "equal",
        "Value": ["www.test.com"],
        "IgnoreCase": True
    })
    return condition

def condition_client_ip() -> BaseCondition:
    """
    条件： 客户端IP匹配，等于 1.1.1.1，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "client_ip",
        "Operator": "match",
        "Value": ["1.1.1.1"]
    })
    return condition

def condition_http_origin() -> BaseCondition:
    """
    条件： HTTP Origin 匹配，等于 www.test.com，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "http_origin",
        "Operator": "equal",
        "Value": ["www.test.com"],
        "IgnoreCase": True
    })
    return condition

def condition_http_user_agent() -> BaseCondition:
    """
    条件： HTTP User-Agent 匹配，等于 Mozilla，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "http_ua",
        "Operator": "equal",
        "Value": ["Mozilla"],
        "IgnoreCase": True
    })
    return condition

def condition_request_header() -> BaseCondition:
    """
    条件： 请求头匹配，请求头 X-H1 等于 1，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "request_header",
        "Operator": "equal",
        "Value": ["1"],
        "IgnoreCase": True,
        "Name": "X-H1"
    })
    return condition

def condition_client_area() -> BaseCondition:
    """
    条件： 客户端地区匹配，等于 CN
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "client_area",
        "Operator": "match",
        "Value": ["CN"]
    })
    return condition

def condition_http_method() -> BaseCondition:
    """
    条件： HTTP Method 匹配，等于 GET
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "http_method",
        "Operator":"equal",
        "Value": ["get"]
    })
    return condition

def condition_request_time() -> BaseCondition:
    """
    条件： 请求时间匹配，每天09:00-20:00，东八区时间
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "request_time",
        "Operator": "match",
        "Value": ["09:00:00", "21:00:00"],
        "TimeZone": "+0800",
        "Name": "everyday"
    })
    return condition

def condition_protocol() -> BaseCondition:
    """
    条件： 协议匹配，等于 http
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "protocol",
        "Operator":"equal",
        "Value": ["http"]
    })
    return condition

def condition_response_header() -> BaseCondition:
    """
    条件： 源站响应头匹配，响应头 X-H1 等于 1，忽略大小写
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object":"response_header",
        "Operator": "equal",
        "Value": ["1"],
        "IgnoreCase": True,
        "Name": "X-H1"
    })
    return condition

def condition_http_code() -> BaseCondition:
    """
    条件： 源站响应状态码匹配，等于 200
    :return: BaseCondition
    """
    condition = BaseCondition({
        "Object": "http_code",
        "Operator":"match",
        "Value": ["200"]
    })
    return condition