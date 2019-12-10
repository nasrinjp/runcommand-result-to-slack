# SSM RunCommandの結果をSlackに通知する
（現状、AWS-InstallMissingWindowsUpdatesドキュメントのみ対応してます）

## Lambda
### 実行ロールのポリシー
role-policy.jsonを参照。
CloudWatch Logsへの出力ポリシーは必要に応じて追加してください。 

### 環境変数
|変数名|値|
|-|-|
|SlackUrl|SlackのWebhookのURL(KMS CMKで暗号化必須)|


## EventBridge
### イベントパターン

```
{
  "source": [
    "aws.ssm"
  ],
  "detail-type": [
    "EC2 Command Invocation Status-change Notification"
  ],
  "detail": {
    "status": [
      "TimedOut",
      "Cancelled",
      "Failed",
      "Success"
    ]
  }
}
```

### ターゲット
実行するLambda関数を指定する
