@Widget
@Component
struct ThinkCheckWidget {
  @LocalStorageProp('latestH') latestH: number = 0
  @LocalStorageProp('latestVerdict') latestVerdict: string = '--'

  build() {
    Column() {
      Text('ThinkCheck 推理健康度').fontSize(14).fontWeight(FontWeight.Bold)
      Text(`H = ${this.latestH.toFixed(2)}`).fontSize(24).fontColor(this.latestH > 0.4 ? '#34C759' : '#FF3B30')
      Text(`判定：${this.latestVerdict}`).fontSize(11).fontColor('#FF9500').margin({ top: 4 })
      Text('点击查看详情 >').fontSize(10).fontColor('#007AFF').margin({ top: 8 })
    }.width('100%').padding(12).alignItems(HorizontalAlign.Center).onClick(() => {
      postCardAction(this, { 'action': 'router', 'bundleName': 'com.thinkcheck.harmony', 'abilityName': 'EntryAbility' })
    })
  }
}