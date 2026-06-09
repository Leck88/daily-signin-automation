# Daily Sign-in Automation

一个面向安卓真机的通用每日签到、领积分、领奖励自动化服务。

项目基于 `adb` + `uiautomator2`，通过模拟手机操作完成低频、可见、可回退的签到类任务。适合个人本地使用、备用机定时运行、学习安卓 UI 自动化。

> 不建议用于批量账号、绕过平台规则、支付、下单、充值、借贷、抢票、强秒杀等高风险场景。

## 功能

- 通过 ADB 自动选择或指定安卓设备。
- 使用 YAML 配置每日任务。
- 支持打开 App、点击文字、点击多个候选文字、滑动、等待、返回、截图。
- 默认风险拦截：命中支付、下单、购买、充值、借款、授权、邀请好友等关键词会跳过点击。
- 支持 dry-run 预演模式，只识别步骤，不执行真实点击。
- 每次运行输出日志，异常时自动截图。
- 支持单次运行或循环调度。

## 适合做什么

- 淘宝、京东、支付宝、闲鱼、美团、航司、酒店、社区类每日签到。
- 会员积分、每日奖励、低风险福利领取。
- 个人安卓 App 自动化测试。

## 不适合做什么

- 抢购/秒杀成功率承诺。
- 自动支付、自动下单、自动充值。
- 多账号批量刷奖励。
- 违反平台规则的自动化。

## 环境要求

- Python 3.10+
- Android 手机开启 USB 调试。
- 已安装 ADB 并加入 PATH。
- 手机上目标 App 已登录。

安装依赖：

```bash
pip install -r requirements.txt
```

检查设备：

```bash
adb devices
```

复制配置：

```bash
copy config\tasks.example.yaml config\tasks.yaml
```

先 dry-run：

```bash
python -m signin_service.cli run --config config\tasks.yaml --dry-run
```

确认无误后真实执行：

```bash
python -m signin_service.cli run --config config\tasks.yaml --execute
```

循环调度：

```bash
python -m signin_service.cli schedule --config config\tasks.yaml --execute
```

## 配置示例

```yaml
tasks:
  - name: 支付宝会员签到
    app: com.eg.android.AlipayGphone
    enabled: true
    schedule: "08:30"
    steps:
      - action: click_text
        text: 我的
      - action: click_text_any
        texts: ["支付宝会员", "会员"]
      - action: click_text_any
        texts: ["签到", "领积分", "立即领取"]
      - action: screenshot
        name: alipay_done
```

## 具象示例：支付宝会员每日签到

仓库内置了一个更具体的支付宝会员签到配置：

```bash
python -m signin_service.cli run --config config\alipay.member.yaml --dry-run
python -m signin_service.cli run --config config\alipay.member.yaml --execute
```

它会按以下流程执行：

1. 打开支付宝。
2. 点击“我的”。
3. 进入“支付宝会员/会员”。
4. 查找“签到、领积分、立即领取、领取”等低风险按钮。
5. 命中支付、下单、充值、授权、开通、借款等关键词时自动跳过。
6. 保存结果截图到 `logs/screenshots`。

如果你要适配其他 App，建议复制 `config/alipay.member.yaml`，只改包名、任务名和步骤文案。

## 安全策略

默认危险关键词：

```text
支付、付款、购买、下单、立即买、提交订单、确认订单、充值、借款、贷款、授权、开通、免密、邀请、助力
```

如果按钮或附近任务名命中这些词，点击会被跳过。你可以在配置里扩展：

```yaml
safety:
  extra_block_keywords:
    - 砍价
    - 拼团
```

## 抢购说明

本项目可以做“打开 App、进入页面、等待按钮出现、辅助点击”的自动化，但不保证抢购成功。真实抢购受库存、网络、风控、验证码、支付确认等因素影响，UI 自动化不是可靠秒杀方案。

## 与 coin11-tb 的关系

这个项目参考了 `coin11-tb` 的安卓 UI 自动化思路，但改造成了通用任务引擎：

- 从“每个平台一个长脚本”改为“配置驱动”。
- 默认增加风险关键词拦截。
- 增加 dry-run、日志、截图、调度。
- 更适合扩展到不同 App 的签到和奖励领取。
